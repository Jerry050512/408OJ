# -*- coding: utf-8 -*-
"""408OJ Web 应用：页面路由 + JSON API。"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import markdown
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .. import config, db, judge, seed

TPL_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

class SubmitBody(BaseModel):
    code: str


class RunBody(BaseModel):
    problem_code: str
    code: str
    input: str = ""


VERDICT_META = {
    "AC": ("通过", "v-ac"), "WA": ("答案错误", "v-wa"), "TLE": ("运行超时", "v-tle"),
    "RE": ("运行错误", "v-re"), "CE": ("编译失败", "v-ce"), "SE": ("系统错误", "v-se"),
    "MLE": ("内存超限", "v-tle"),
}


import re

def md(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'#include\s*<([^>]+)>', r'#include &lt;\1&gt;', text)
    return markdown.markdown(text, extensions=["fenced_code", "tables", "nl2br"])


def create_app(db_path: Path | None = None, do_seed: bool = True) -> FastAPI:
    db_path = Path(db_path or config.DB_PATH)
    app = FastAPI(title="408OJ", docs_url=None, redoc_url=None)

    templates = Jinja2Templates(directory=str(TPL_DIR))
    templates.env.filters["md"] = md

    def _dt(ts) -> str:
        return time.strftime("%m-%d %H:%M", time.localtime(float(ts)))

    def _stars(n: int) -> str:
        n = max(1, min(5, int(n)))
        return "★" * n + "<span class='off'>" + "★" * (5 - n) + "</span>"

    templates.env.filters["datetime"] = _dt
    templates.env.globals["verdict_meta"] = VERDICT_META
    templates.env.globals["stars"] = _stars
    templates.env.globals["site"] = {"title": config.WEB_TITLE}

    def conn() -> sqlite3.Connection:
        c = db.connect(db_path)
        return c

    if do_seed:
        c = conn()
        try:
            cnt = c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='problems'").fetchone()[0]
            need = True
            if cnt:
                need = c.execute("SELECT COUNT(*) FROM problems").fetchone()[0] == 0
            if need:
                seed.seed_database(c)
        finally:
            c.close()

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # ---------------- 辅助 ----------------

    def solved_map(c):
        return db.solved_problem_ids(c)

    def ctx_status(c, problems):
        smap = solved_map(c)
        for p in problems:
            v = smap.get(p["id"])
            p["status"] = "solved" if v == "AC" else ("tried" if v else "")
        return problems

    # ---------------- 页面 ----------------

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        c = conn()
        try:
            problems = db.list_problems(c)
            smap = db.solved_problem_ids(c)
            exam = [p for p in problems if p["kind"] == "exam"]
            prac = [p for p in problems if p["kind"] == "practice"]
            solved_exam = sum(1 for p in exam if smap.get(p["id"]) == "AC")
            solved_prac = sum(1 for p in prac if smap.get(p["id"]) == "AC")
            tried = sum(1 for v in smap.values() if v and v != "AC")
            recent = db.list_submissions(c, limit=6)
            for s in recent:
                s["p"] = db.get_problem_by_id(c, s["problem_id"])
            chapters = {}
            for p in problems:
                ch = chapters.setdefault(p["chapter"], {"total": 0, "solved": 0})
                ch["total"] += 1
                if smap.get(p["id"]) == "AC":
                    ch["solved"] += 1
            return templates.TemplateResponse(request, "index.html", {
                "problems": problems, "exam": exam, "prac": prac,
                "solved_exam": solved_exam, "solved_prac": solved_prac,
                "total_sub": c.execute("SELECT COUNT(*) FROM submissions").fetchone()[0],
                "ac_sub": c.execute("SELECT COUNT(*) FROM submissions WHERE verdict='AC'").fetchone()[0],
                "tried": tried, "recent": recent, "chapters": chapters,
                "page": "home",
            })
        finally:
            c.close()

    @app.get("/problems", response_class=HTMLResponse)
    def problems_page(request: Request, kind: str = "", chapter: str = "",
                      tag: str = "", q: str = "", diff: int = 0, status: str = ""):
        c = conn()
        try:
            problems = ctx_status(c, db.list_problems(
                c, kind=kind or None, chapter=chapter or None,
                tag=tag or None, difficulty=diff or None, q=q or None))
            if status == "solved":
                problems = [p for p in problems if p["status"] == "solved"]
            elif status == "unsolved":
                problems = [p for p in problems if p["status"] != "solved"]
            return templates.TemplateResponse(request, "problems.html", {
                "problems": problems, "chapters": db.chapters(c), "tags": db.all_tags(c),
                "f": {"kind": kind, "chapter": chapter, "tag": tag, "q": q,
                      "diff": diff, "status": status},
                "page": "problems",
            })
        finally:
            c.close()

    @app.get("/p/{code}", response_class=HTMLResponse)
    def problem_page(request: Request, code: str):
        c = conn()
        try:
            p = db.get_problem(c, code)
            if not p:
                return templates.TemplateResponse(request, "error.html",
                                                  {"msg": "题目不存在", "page": ""}, status_code=404)
            sm = db.solved_problem_ids(c).get(p["id"])
            subs = db.list_submissions(c, problem_id=p["id"], limit=8)
            return templates.TemplateResponse(request, "problem.html", {
                "p": p, "status": "solved" if sm == "AC" else ("tried" if sm else ""),
                "subs": subs, "page": "problems",
            })
        finally:
            c.close()

    @app.get("/p/{code}/solution", response_class=HTMLResponse)
    def solution_page(request: Request, code: str):
        c = conn()
        try:
            p = db.get_problem(c, code)
            if not p:
                return templates.TemplateResponse(request, "error.html",
                                                  {"msg": "题目不存在", "page": ""}, status_code=404)
            return templates.TemplateResponse(request, "solution.html",
                                              {"p": p, "page": "problems"})
        finally:
            c.close()

    @app.get("/submissions", response_class=HTMLResponse)
    def submissions_page(request: Request, problem: str = ""):
        c = conn()
        try:
            pid = None
            p = None
            if problem:
                p = db.get_problem(c, problem)
                pid = p["id"] if p else None
            subs = db.list_submissions(c, problem_id=pid, limit=100)
            return templates.TemplateResponse(request, "submissions.html", {
                "subs": subs, "problem": p, "page": "submissions"})
        finally:
            c.close()

    @app.get("/s/{sid}", response_class=HTMLResponse)
    def submission_page(request: Request, sid: int):
        c = conn()
        try:
            s = db.get_submission(c, sid)
            if not s:
                return templates.TemplateResponse(request, "error.html",
                                                  {"msg": "提交记录不存在", "page": ""}, status_code=404)
            s["p"] = db.get_problem_by_id(c, s["problem_id"])
            return templates.TemplateResponse(request, "submission.html",
                                              {"s": s, "page": "submissions"})
        finally:
            c.close()

    @app.get("/stats", response_class=HTMLResponse)
    def stats_page(request: Request):
        c = conn()
        try:
            problems = db.list_problems(c)
            smap = db.solved_problem_ids(c)
            chapters = {}
            for p in problems:
                ch = chapters.setdefault(p["chapter"], {"total": 0, "solved": 0, "exam": 0, "exam_solved": 0})
                ch["total"] += 1
                ch["exam"] += p["kind"] == "exam"
                if smap.get(p["id"]) == "AC":
                    ch["solved"] += 1
                    ch["exam_solved"] += p["kind"] == "exam"
            tagfreq = {}
            for p in problems:
                for t in p["tags"]:
                    tagfreq[t] = tagfreq.get(t, 0) + 1
            tagfreq = sorted(tagfreq.items(), key=lambda kv: -kv[1])
            years = {}
            for p in problems:
                if p["kind"] == "exam":
                    years[p["year"]] = "AC" if smap.get(p["id"]) == "AC" else years.get(p["year"], "")
            subs = db.list_submissions(c, limit=500)
            return templates.TemplateResponse(request, "stats.html", {
                "chapters": chapters, "tagfreq": tagfreq, "years": sorted(years.items()),
                "subs": subs, "page": "stats",
            })
        finally:
            c.close()

    # ---------------- API ----------------

    @app.get("/api/v1/problems")
    def api_problems(kind: str = "", chapter: str = "", tag: str = "", q: str = ""):
        c = conn()
        try:
            ps = ctx_status(c, db.list_problems(
                c, kind=kind or None, chapter=chapter or None, tag=tag or None, q=q or None))
            return [{"code": p["code"], "title": p["title"], "kind": p["kind"],
                     "year": p["year"], "chapter": p["chapter"], "tags": p["tags"],
                     "difficulty": p["difficulty"], "importance": p["importance"],
                     "status": p["status"]} for p in ps]
        finally:
            c.close()

    @app.get("/api/v1/problems/{code}")
    def api_problem(code: str):
        c = conn()
        try:
            p = db.get_problem(c, code)
            if not p:
                return JSONResponse({"error": "not found"}, status_code=404)
            return {
                "code": p["code"], "title": p["title"], "kind": p["kind"],
                "year": p["year"], "exam_no": p["exam_no"], "chapter": p["chapter"],
                "tags": p["tags"], "difficulty": p["difficulty"], "importance": p["importance"],
                "statement_md": p["statement_md"], "input_md": p["input_md"],
                "output_md": p["output_md"], "samples": p["samples"],
                "policy": p["policy"], "lang_hint": p["lang_hint"],
                "time_limit_ms": p["time_limit_ms"], "memory_limit_kb": p["memory_limit_kb"],
            }
        finally:
            c.close()

    @app.post("/api/v1/problems/{code}/submit")
    def api_submit(code: str, body: SubmitBody):
        src = body.code
        if len(src.encode("utf-8")) > config.MAX_SOURCE_BYTES:
            return JSONResponse({"error": "代码超过大小限制"}, status_code=400)
        c = conn()
        try:
            p = db.get_problem(c, code)
            if not p:
                return JSONResponse({"error": "not found"}, status_code=404)
            cases = db.get_testcases(c, p["id"])
            r = judge.judge_code(src, p["policy"], cases,
                                 p["time_limit_ms"], p["memory_limit_kb"])
            sid = db.create_submission(
                c, p["id"], src, r["verdict"], r["passed"], r["total"],
                r["max_time_ms"], r["max_mem_kb"], r["compile_msg"],
                r["results"][:config.GIT_KEEP_FULL_RESULTS], r["policy_issues"])
            return {"id": sid, "verdict": r["verdict"], "passed": r["passed"],
                    "total": r["total"], "max_time_ms": round(r["max_time_ms"], 1),
                    "max_mem_kb": r["max_mem_kb"], "compile_msg": r["compile_msg"][:3000],
                    "policy_issues": r["policy_issues"]}
        finally:
            c.close()

    @app.get("/api/v1/submissions/{sid}")
    def api_submission(sid: int):
        c = conn()
        try:
            s = db.get_submission(c, sid)
            if not s:
                return JSONResponse({"error": "not found"}, status_code=404)
            s["problem_code"] = db.get_problem_by_id(c, s["problem_id"])["code"]
            return s
        finally:
            c.close()

    @app.post("/api/v1/run")
    def api_run(body: RunBody):
        if len(body.input.encode("utf-8")) > config.MAX_CUSTOM_INPUT_BYTES:
            return JSONResponse({"error": "输入过大"}, status_code=400)
        c = conn()
        try:
            p = db.get_problem(c, body.problem_code)
            if not p:
                return JSONResponse({"error": "not found"}, status_code=404)
            r = judge.run_custom(body.code, p["policy"], body.input,
                                 p["time_limit_ms"], p["memory_limit_kb"])
            return r
        finally:
            c.close()

    @app.get("/api/v1/stats")
    def api_stats():
        c = conn()
        try:
            total = c.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
            subs = c.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
            ac = c.execute("SELECT COUNT(*) FROM submissions WHERE verdict='AC'").fetchone()[0]
            solved = len([1 for v in db.solved_problem_ids(c).values() if v == "AC"])
            return {"problems": total, "submissions": subs, "ac": ac, "solved": solved}
        finally:
            c.close()

    @app.get("/favicon.ico")
    def favicon():
        return RedirectResponse("/static/favicon.svg")

    return app


app = create_app()

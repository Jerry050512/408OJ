# -*- coding: utf-8 -*-
"""408OJ 静态页面生成器 (Static Site Exporter).

将 Jinja2 模板与题库数据预渲染为纯静态 HTML 页面并置于 dist/ 目录，
支持直接部署于 Vercel / Cloudflare Pages / Render / GitHub Pages。
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import time
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

from oj import config, db, seed

ROOT_DIR = Path(__file__).parent
TPL_DIR = ROOT_DIR / "oj" / "web" / "templates"
STATIC_DIR = ROOT_DIR / "oj" / "web" / "static"
DIST_DIR = ROOT_DIR / "dist"

VERDICT_META = {
    "AC": ("通过", "v-ac"), "WA": ("答案错误", "v-wa"), "TLE": ("运行超时", "v-tle"),
    "RE": ("运行错误", "v-re"), "CE": ("编译失败", "v-ce"), "SE": ("系统错误", "v-se"),
    "MLE": ("内存超限", "v-tle"),
}


def md(text: str) -> str:
    return markdown.markdown(text or "", extensions=["fenced_code", "tables", "nl2br"])


def _dt(ts) -> str:
    return time.strftime("%m-%d %H:%M", time.localtime(float(ts)))


def _stars(n: int) -> str:
    n = max(1, min(5, int(n)))
    return "★" * n + "<span class='off'>" + "★" * (5 - n) + "</span>"


def build_static_site() -> None:
    print("🚀 开始构建 408OJ 纯静态全站...")

    # 清理并创建 dist/
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 复制 static/ 资源
    dist_static = DIST_DIR / "static"
    shutil.copytree(STATIC_DIR, dist_static)

    # 复制 picoc WASM UMD bundle
    picoc_src = ROOT_DIR / "node_modules" / "picoc-js" / "dist" / "bundle.umd.js"
    if picoc_src.exists():
        shutil.copy(picoc_src, dist_static / "js" / "picoc.umd.js")
        print("  ✓ 已打包 picoc.umd.js 至 static/js/")

    # 2. 内存建库并加载题库数据
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    seed.seed_database(conn)

    problems = db.list_problems(conn)
    smap = db.solved_problem_ids(conn)
    exam = [p for p in problems if p["kind"] == "exam"]
    prac = [p for p in problems if p["kind"] == "practice"]
    chapters_data = {}
    for p in problems:
        ch = chapters_data.setdefault(p["chapter"], {"total": 0, "solved": 0, "exam": 0, "exam_solved": 0})
        ch["total"] += 1
        ch["exam"] += (p["kind"] == "exam")

    # 导出 API 数据 (JSON)
    api_dir = DIST_DIR / "api" / "v1"
    (api_dir / "problems").mkdir(parents=True, exist_ok=True)

    problems_json = []
    for p in problems:
        p_cases = db.get_testcases(conn, p["id"])
        p["testcases"] = p_cases
        p_data = {
            "code": p["code"], "title": p["title"], "kind": p["kind"],
            "year": p["year"], "exam_no": p["exam_no"], "chapter": p["chapter"],
            "tags": p["tags"], "difficulty": p["difficulty"], "importance": p["importance"],
            "statement_md": p["statement_md"], "input_md": p["input_md"],
            "output_md": p["output_md"], "samples": p["samples"],
            "policy": p["policy"], "lang_hint": p["lang_hint"],
            "time_limit_ms": p["time_limit_ms"], "memory_limit_kb": p["memory_limit_kb"],
            "testcases": p_cases
        }
        problems_json.append(p_data)
        with open(api_dir / "problems" / f"{p['code']}.json", "w", encoding="utf-8") as f:
            json.dump(p_data, f, ensure_ascii=False, indent=2)

    with open(api_dir / "problems.json", "w", encoding="utf-8") as f:
        json.dump(problems_json, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 已导出 {len(problems)} 道题目的 JSON 数据库至 api/v1/")

    # 3. 初始化 Jinja2 渲染环境
    env = Environment(loader=FileSystemLoader(str(TPL_DIR)))
    env.filters["md"] = md
    env.filters["datetime"] = _dt
    env.globals["verdict_meta"] = VERDICT_META
    env.globals["stars"] = _stars
    env.globals["site"] = {"title": config.WEB_TITLE}

    def render_page(tpl_name: str, ctx: dict, out_path: Path) -> None:
        ctx["STATIC_MODE"] = True
        template = env.get_template(tpl_name)
        html = template.render(**ctx)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

    # 渲染 index.html
    render_page("index.html", {
        "problems": problems, "exam": exam, "prac": prac,
        "solved_exam": 0, "solved_prac": 0, "total_sub": 0,
        "ac_sub": 0, "tried": 0, "recent": [], "chapters": chapters_data,
        "page": "home"
    }, DIST_DIR / "index.html")

    # 渲染 problems/index.html
    render_page("problems.html", {
        "problems": problems, "chapters": db.chapters(conn), "tags": db.all_tags(conn),
        "f": {"kind": "", "chapter": "", "tag": "", "q": "", "diff": 0, "status": ""},
        "page": "problems"
    }, DIST_DIR / "problems" / "index.html")

    # 渲染每道题的 problem.html & solution.html
    for p in problems:
        p_dir = DIST_DIR / "p" / p["code"]
        render_page("problem.html", {
            "p": p, "status": "", "subs": [], "page": "problems"
        }, p_dir / "index.html")

        render_page("solution.html", {
            "p": p, "page": "problems"
        }, p_dir / "solution" / "index.html")

    # 渲染 submissions/index.html & s/index.html
    render_page("submissions.html", {
        "subs": [], "problem": None, "page": "submissions"
    }, DIST_DIR / "submissions" / "index.html")

    # 渲染 stats/index.html
    tagfreq = {}
    for p in problems:
        for t in p["tags"]:
            tagfreq[t] = tagfreq.get(t, 0) + 1
    tagfreq = sorted(tagfreq.items(), key=lambda kv: -kv[1])
    years = sorted({(p["year"], "") for p in problems if p["kind"] == "exam"})

    render_page("stats.html", {
        "chapters": chapters_data, "tagfreq": tagfreq, "years": years,
        "subs": [], "page": "stats"
    }, DIST_DIR / "stats" / "index.html")

    # 渲染 error.html 作为 404.html
    render_page("error.html", {
        "msg": "页面不存在或已被移除", "page": ""
    }, DIST_DIR / "404.html")

    conn.close()
    print("🎉 静态全站生成完成！渲染产物存放在 dist/ 目录。")


if __name__ == "__main__":
    build_static_site()

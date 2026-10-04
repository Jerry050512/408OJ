# -*- coding: utf-8 -*-
"""题库构建：把 content 中的题目写入数据库，并用参考实现生成期望输出。"""
from __future__ import annotations

import hashlib

from . import db
from .content import real_2012_2016, real_2017_2021, real_2022_2026
from .content import practice

CONTENT_MODULES = [real_2012_2016, real_2017_2021, real_2022_2026, practice]


def all_problem_defs() -> list[dict]:
    out: list[dict] = []
    for mod in CONTENT_MODULES:
        out.extend(mod.PROBLEMS)
    return out


def _norm_text(s: str) -> str:
    s = s.replace("\r\n", "\n")
    return s if s.endswith("\n") else s + "\n"


def build_testcases(pdef: dict) -> list[dict]:
    """样例 + 生成器测试点；期望输出由 ref_py 计算。"""
    cases: list[dict] = []
    seen = set()

    def add(inp: str, is_sample: bool, expected: str | None):
        inp = _norm_text(inp)
        key = hashlib.md5(inp.encode()).hexdigest()
        if key in seen:
            return
        seen.add(key)
        if expected is None:
            expected = pdef["ref_py"](inp)
        cases.append({"input": inp, "expected": _norm_text(expected),
                      "is_sample": int(is_sample)})

    for s in pdef.get("samples", []):
        add(s["input"], True, s.get("output"))
    gen = pdef.get("gen")
    if gen:
        seed = int(hashlib.md5(pdef["code"].encode()).hexdigest()[:8], 16)
        for inp in gen(seed):
            add(inp, False, None)
    return cases


def seed_database(conn) -> int:
    """幂等填充题库。返回题目数。"""
    db.init_db(conn)
    for idx, pdef in enumerate(all_problem_defs()):
        samples = pdef.get("samples", [])
        # 校验：手写样例输出必须与参考实现一致（在 seed 阶段就暴露内容错误）
        for s in samples:
            expect = _norm_text(pdef["ref_py"](_norm_text(s["input"])))
            got = _norm_text(s.get("output", ""))
            if expect != got:
                raise ValueError(
                    f"题目 {pdef['code']} 样例输出与参考实现不一致：\n"
                    f"输入:\n{s['input']}\n参考实现:\n{expect}\n题面样例:\n{got}")
        cases = build_testcases(pdef)
        row = {
            "code": pdef["code"], "title": pdef["title"], "kind": pdef["kind"],
            "year": pdef.get("year"), "exam_no": pdef.get("exam_no", ""),
            "chapter": pdef["chapter"], "tags": pdef.get("tags", []),
            "difficulty": pdef.get("difficulty", 2),
            "importance": pdef.get("importance", 3),
            "statement_md": pdef["statement_md"],
            "input_md": pdef.get("input_md", ""), "output_md": pdef.get("output_md", ""),
            "samples": [{"input": _norm_text(s["input"]),
                         "output": _norm_text(pdef["ref_py"](_norm_text(s["input"])))}
                        for s in samples],
            "time_limit_ms": pdef.get("time_limit_ms", 1000),
            "memory_limit_kb": pdef.get("memory_limit_kb", 64 * 1024),
            "policy": pdef.get("policy", {"level": "standard"}),
            "solution_md": pdef.get("solution_md", ""),
            "lang_hint": pdef.get("lang_hint", ""),
            "ref_solution_c": pdef.get("ref_c", ""),
            "ord": idx,
        }
        pid = db.upsert_problem(conn, row)
        db.replace_testcases(conn, pid, cases)
        conn.commit()
    return len(all_problem_defs())

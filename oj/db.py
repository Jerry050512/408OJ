"""SQLite 数据访问层。"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,          -- real-2013-41 / prac-link-01
    title TEXT NOT NULL,
    kind TEXT NOT NULL,                 -- exam / practice
    year INTEGER,
    exam_no TEXT,                       -- 原题号，如 "第41题"
    chapter TEXT NOT NULL,              -- 线性表/栈队列串/树与二叉树/图/查找与排序/综合
    tags TEXT NOT NULL DEFAULT '[]',
    difficulty INTEGER NOT NULL DEFAULT 2,   -- 1 易 2 中 3 难
    importance INTEGER NOT NULL DEFAULT 3,   -- 1..5 考点重要度
    statement_md TEXT NOT NULL,
    input_md TEXT NOT NULL DEFAULT '',
    output_md TEXT NOT NULL DEFAULT '',
    samples TEXT NOT NULL DEFAULT '[]',      -- [{input, output}]
    time_limit_ms INTEGER NOT NULL DEFAULT 1000,
    memory_limit_kb INTEGER NOT NULL DEFAULT 65536,
    policy TEXT NOT NULL DEFAULT '{}',
    solution_md TEXT NOT NULL DEFAULT '',
    lang_hint TEXT NOT NULL DEFAULT '',
    ref_solution_c TEXT NOT NULL DEFAULT '',
    ord INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS testcases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    ord INTEGER NOT NULL,
    input TEXT NOT NULL,
    expected TEXT NOT NULL,
    is_sample INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_testcases_pid ON testcases(problem_id, ord);
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    verdict TEXT NOT NULL DEFAULT 'PD',
    passed INTEGER NOT NULL DEFAULT 0,
    total INTEGER NOT NULL DEFAULT 0,
    max_time_ms REAL NOT NULL DEFAULT 0,
    max_mem_kb REAL NOT NULL DEFAULT 0,
    compile_msg TEXT NOT NULL DEFAULT '',
    results TEXT NOT NULL DEFAULT '[]',
    policy_issues TEXT NOT NULL DEFAULT '[]',
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sub_pid ON submissions(problem_id, id DESC);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


# ---------- problems ----------

def upsert_problem(conn: sqlite3.Connection, p: dict[str, Any]) -> int:
    cols = ["code", "title", "kind", "year", "exam_no", "chapter", "tags", "difficulty",
            "importance", "statement_md", "input_md", "output_md", "samples",
            "time_limit_ms", "memory_limit_kb", "policy", "solution_md", "lang_hint",
            "ref_solution_c", "ord"]
    row = dict(p)
    row["tags"] = json.dumps(row.get("tags", []), ensure_ascii=False)
    row["samples"] = json.dumps(row.get("samples", []), ensure_ascii=False)
    row["policy"] = json.dumps(row.get("policy", {}), ensure_ascii=False)
    placeholders = ",".join("?" for _ in cols)
    updates = ",".join(f"{c}=excluded.{c}" for c in cols if c != "code")
    cur = conn.execute(
        f"INSERT INTO problems({','.join(cols)}) VALUES({placeholders}) "
        f"ON CONFLICT(code) DO UPDATE SET {updates}",
        [row.get(c) for c in cols],
    )
    pid = row.get("id")
    if pid is None:
        pid = conn.execute("SELECT id FROM problems WHERE code=?", (row["code"],)).fetchone()[0]
    return pid


def replace_testcases(conn: sqlite3.Connection, problem_id: int, cases: Iterable[dict]) -> None:
    conn.execute("DELETE FROM testcases WHERE problem_id=?", (problem_id,))
    conn.executemany(
        "INSERT INTO testcases(problem_id, ord, input, expected, is_sample) VALUES(?,?,?,?,?)",
        [(problem_id, i, c["input"], c["expected"], int(c.get("is_sample", 0)))
         for i, c in enumerate(cases)],
    )


def get_problem(conn: sqlite3.Connection, code: str) -> dict | None:
    r = conn.execute("SELECT * FROM problems WHERE code=?", (code,)).fetchone()
    return _decode_problem(r) if r else None


def get_problem_by_id(conn: sqlite3.Connection, pid: int) -> dict | None:
    r = conn.execute("SELECT * FROM problems WHERE id=?", (pid,)).fetchone()
    return _decode_problem(r) if r else None


def list_problems(conn: sqlite3.Connection, kind=None, chapter=None, tag=None,
                  difficulty=None, q=None) -> list[dict]:
    sql = "SELECT * FROM problems WHERE 1=1"
    args: list[Any] = []
    if kind:
        sql += " AND kind=?"; args.append(kind)
    if chapter:
        sql += " AND chapter=?"; args.append(chapter)
    if difficulty:
        sql += " AND difficulty=?"; args.append(difficulty)
    if q:
        sql += " AND (title LIKE ? OR code LIKE ?)"
        args += [f"%{q}%", f"%{q}%"]
    sql += " ORDER BY ord, code"
    rows = [ _decode_problem(r) for r in conn.execute(sql, args) ]
    if tag:
        rows = [p for p in rows if tag in p["tags"]]
    return rows


def get_testcases(conn: sqlite3.Connection, problem_id: int) -> list[dict]:
    return [dict(r) for r in conn.execute(
        "SELECT * FROM testcases WHERE problem_id=? ORDER BY ord", (problem_id,))]


def chapters(conn: sqlite3.Connection) -> list[str]:
    return [r[0] for r in conn.execute("SELECT DISTINCT chapter FROM problems ORDER BY chapter")]


def all_tags(conn: sqlite3.Connection) -> list[str]:
    tags: set[str] = set()
    for r in conn.execute("SELECT tags FROM problems"):
        tags.update(json.loads(r[0]))
    return sorted(tags)


def _decode_problem(r: sqlite3.Row) -> dict:
    p = dict(r)
    p["tags"] = json.loads(p["tags"])
    p["samples"] = json.loads(p["samples"])
    p["policy"] = json.loads(p["policy"])
    return p


# ---------- submissions ----------

def create_submission(conn: sqlite3.Connection, problem_id: int, code: str,
                      verdict: str, passed: int, total: int, max_time_ms: float,
                      max_mem_kb: float, compile_msg: str, results: list,
                      policy_issues: list) -> int:
    cur = conn.execute(
        "INSERT INTO submissions(problem_id, code, verdict, passed, total, max_time_ms,"
        " max_mem_kb, compile_msg, results, policy_issues, created_at)"
        " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (problem_id, code, verdict, passed, total, max_time_ms, max_mem_kb, compile_msg,
         json.dumps(results, ensure_ascii=False),
         json.dumps(policy_issues, ensure_ascii=False), time.time()),
    )
    conn.commit()
    return cur.lastrowid


def get_submission(conn: sqlite3.Connection, sid: int) -> dict | None:
    r = conn.execute("SELECT * FROM submissions WHERE id=?", (sid,)).fetchone()
    return _decode_sub(r) if r else None


def list_submissions(conn: sqlite3.Connection, problem_id=None, limit=50, offset=0) -> list[dict]:
    sql = ("SELECT s.*, p.code AS problem_code, p.title AS problem_title FROM submissions s"
           " JOIN problems p ON p.id=s.problem_id")
    args: list[Any] = []
    if problem_id:
        sql += " WHERE s.problem_id=?"; args.append(problem_id)
    sql += " ORDER BY s.id DESC LIMIT ? OFFSET ?"
    args += [limit, offset]
    return [_decode_sub(r) for r in conn.execute(sql, args)]


def _decode_sub(r: sqlite3.Row) -> dict:
    s = dict(r)
    s["results"] = json.loads(s["results"])
    s["policy_issues"] = json.loads(s["policy_issues"])
    return s


def solved_problem_ids(conn: sqlite3.Connection) -> dict[int, str]:
    """problem_id -> 最好成绩 verdict（AC 优先）。"""
    out: dict[int, str] = {}
    for r in conn.execute("SELECT problem_id, verdict FROM submissions ORDER BY id"):
        pid, v = r[0], r[1]
        if out.get(pid) != "AC":
            out[pid] = v
    return out

# -*- coding: utf-8 -*-
"""题库完整性测试：样例一致性、字段齐全、参考解全部 AC（集成）。"""
import pytest

from oj import db as dbm
from oj import judge, seed


@pytest.fixture(scope="module")
def seeded(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "oj.db"
    conn = dbm.connect(path)
    seed.seed_database(conn)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def pdefs():
    return {p["code"]: p for p in seed.all_problem_defs()}


def test_problem_count(seeded):
    assert len(dbm.list_problems(seeded)) >= 40


def test_exam_problems_cover_all_years(pdefs):
    years = {p["year"] for p in pdefs.values() if p["kind"] == "exam"}
    assert years == set(range(2012, 2027))


def test_all_fields_present(seeded):
    for p in dbm.list_problems(seeded):
        assert p["title"] and p["statement_md"] and p["solution_md"]
        assert p["input_md"] and p["output_md"]
        assert p["chapter"]
        assert 1 <= p["importance"] <= 5
        assert 1 <= p["difficulty"] <= 3
        assert p["tags"]
        assert p["ref_solution_c"].strip().startswith("#include")


def test_each_problem_has_cases(seeded):
    for p in dbm.list_problems(seeded):
        cases = dbm.get_testcases(seeded, p["id"])
        assert len(cases) >= 3, p["code"]
        assert any(c["is_sample"] for c in cases), p["code"]
        for c in cases:
            assert c["expected"].strip() != "" or c["input"].strip() == "", p["code"]


def test_all_tags_registered(seeded):
    assert set(dbm.all_tags(seeded))


@pytest.mark.slow
def test_reference_solutions_all_ac(seeded):
    """每道题的参考 C 解对所有测试点 AC —— 最强的内容正确性保障。"""
    failures = []
    for p in dbm.list_problems(seeded):
        cases = dbm.get_testcases(seeded, p["id"])
        r = judge.judge_code(p["ref_solution_c"], p["policy"], cases,
                             p["time_limit_ms"], p["memory_limit_kb"])
        if r["verdict"] != "AC":
            failures.append((p["code"], r["verdict"], r["compile_msg"][:200]))
    assert not failures, failures


def test_ref_solutions_pass_policy(pdefs):
    """参考解自身必须通过 408 合规检查。"""
    from oj.policy import check_source
    for code, p in pdefs.items():
        issues = check_source(p["ref_c"], p.get("policy"))
        assert not issues, (code, [i.fmt() for i in issues])

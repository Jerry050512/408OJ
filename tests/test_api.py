# -*- coding: utf-8 -*-
"""页面路由与 JSON API 测试（使用独立临时库）。"""

SOLVE_2018 = (
    "#include <stdio.h>\n#include <stdlib.h>\n"
    "int main(void){\n    int n;\n    if (scanf(\"%d\", &n) != 1) return 0;\n"
    "    char *seen = (char*)calloc((size_t)n + 2, 1);\n"
    "    for (int i = 0; i < n; i++){ int x; scanf(\"%d\", &x); if (x >= 1 && x <= n) seen[x] = 1; }\n"
    "    for (int i = 1; i <= n + 1; i++){ if (!seen[i]){ printf(\"%d\\n\", i); break; } }\n"
    "    free(seen);\n    return 0;\n}\n"
)


def test_pages_ok(client):
    for url in ["/", "/problems", "/submissions", "/stats",
                    "/p/real-2018-41", "/p/real-2018-41/solution"]:
        r = client.get(url)
        assert r.status_code == 200, url
        assert "charset" in r.headers["content-type"]


def test_problem_page_content(client):
    r = client.get("/p/real-2018-41")
    assert "未出现的最小正整数" in r.text
    assert "editor" in r.text           # 编辑器
    assert "408 合规约束" in r.text      # 合规说明
    assert "样例" in r.text


def test_problem_404(client):
    assert client.get("/p/no-such-code").status_code == 404
    assert client.get("/api/v1/problems/no-such-code").status_code == 404


def test_api_problems_list(client):
    r = client.get("/api/v1/problems")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 40
    p0 = data[0]
    assert {"code", "title", "kind", "chapter", "tags", "status"} <= set(p0)


def test_api_problems_filter(client):
    exams = client.get("/api/v1/problems?kind=exam").json()
    assert all(p["kind"] == "exam" for p in exams)
    assert {p["year"] for p in exams} == set(range(2012, 2027))
    trees = client.get("/api/v1/problems", params={"chapter": "树与二叉树"}).json()
    assert trees and all(p["chapter"] == "树与二叉树" for p in trees)
    kmp = client.get("/api/v1/problems", params={"tag": "KMP"}).json()
    assert len(kmp) >= 2


def test_api_problem_detail(client):
    p = client.get("/api/v1/problems/real-2018-41").json()
    assert p["samples"][0]["input"] == "4\n-5 3 2 3\n"
    assert p["policy"]["level"] == "standard"
    assert "#include" in p["lang_hint"]


def test_submit_ac(client):
    r = client.post("/api/v1/problems/real-2018-41/submit", json={"code": SOLVE_2018})
    assert r.status_code == 200
    j = r.json()
    assert j["verdict"] == "AC"
    assert j["passed"] == j["total"] > 0
    assert j["id"] > 0


def test_submit_wa_and_policy(client):
    bad = SOLVE_2018.replace("!seen[i]", "seen[i]")
    j = client.post("/api/v1/problems/real-2018-41/submit", json={"code": bad}).json()
    assert j["verdict"] in ("WA", "RE", "TLE")

    illegal = "#include <windows.h>\nint main(){return 0;}"
    j = client.post("/api/v1/problems/real-2018-41/submit", json={"code": illegal}).json()
    assert j["verdict"] == "CE"
    assert j["policy_issues"]


def test_submission_records(client):
    detail = client.get("/api/v1/submissions/1")
    assert detail.status_code == 200
    assert detail.json()["verdict"] == "AC"
    page = client.get("/submissions")
    assert page.status_code == 200 and "real-2018-41" in page.text or "#1" in page.text
    one = client.get("/s/1")
    assert one.status_code == 200 and "评测详情" in one.text


def test_solved_status_propagates(client):
    problems = {p["code"]: p for p in client.get("/api/v1/problems").json()}
    assert problems["real-2018-41"]["status"] == "solved"
    assert problems["real-2019-41"]["status"] == ""


def test_custom_run(client):
    r = client.post("/api/v1/run", json={
        "problem_code": "real-2018-41", "code": SOLVE_2018, "input": "3\n1 2 3\n"})
    j = r.json()
    assert j["ok"] and j["stdout"].strip() == "4"


def test_custom_run_ce(client):
    j = client.post("/api/v1/run", json={
        "problem_code": "real-2018-41", "code": "int main(){", "input": ""}).json()
    assert not j["ok"] and j["stage"] == "compile"


def test_stats_api(client):
    s = client.get("/api/v1/stats").json()
    assert s["problems"] >= 40 and s["solved"] >= 1


def test_solution_page_has_solution(client):
    r = client.get("/p/real-2019-41/solution")
    assert r.status_code == 200
    assert "找中点" in r.text and "复杂度" in r.text


def test_mock_kind_end_to_end(client):
    mocks = client.get("/api/v1/problems?kind=mock").json()
    assert mocks and all(p["kind"] == "mock" for p in mocks)
    n_prac = len(client.get("/api/v1/problems?kind=practice").json())
    r = client.get("/problems", params={"kind": "mock"})
    assert r.status_code == 200
    assert 'value="mock"' in r.text and "b-mock" in r.text  # 筛选项 + 第三类徽章
    r = client.get("/")
    assert "b-mock" in r.text and "模拟 ·" in r.text         # hero 徽章行
    assert "模拟题已通过" in r.text                            # stat-card
    assert f"配 {n_prac} 道拆解练习" in r.text                 # 话术口径动模板变量
    assert 'class="kicker"' not in r.text                    # eyebrow-kicker 禁令


def test_ui_css_regressions():
    import re
    from pathlib import Path
    css = (Path(__file__).parent.parent / "oj/web/static/css/design.css").read_text(encoding="utf-8")
    notice = re.search(r"\.notice\s*\{[^}]*\}", css).group(0)
    assert not re.search(r"border-left\s*:\s*[2-9]", notice)   # 侧边压边=AI 痕迹,禁止回歸
    assert "#8b949e" in css and "#687079" in css              # muted token AA 配色
    assert ".badge.b-mock" in css and ".kicker" not in css


def test_static_and_favicon(client):
    assert client.get("/static/css/design.css").status_code == 200
    assert client.get("/static/js/editor.js").status_code == 200
    assert client.get("/static/favicon.svg").status_code == 200

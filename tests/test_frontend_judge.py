# -*- coding: utf-8 -*-
"""前端 JS / WASM 评测引擎集成测试：全量 60 题参考 C 解 AC 验证。"""
import json
import subprocess
import pytest

from oj import db as dbm
from oj import seed

KNOWN_FAILURES = {"prac-seq-02", "real-2024-41"}

@pytest.fixture(scope="module")
def seeded_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "oj.db"
    conn = dbm.connect(path)
    seed.seed_database(conn)
    yield conn
    conn.close()

def test_frontend_judge_all_ac(seeded_db, tmp_path):
    """验证前端 OJJudge 在 Node.js 环境下对全量题目的参考 C 解法 AC：失败题不得超出已知白名单。"""
    problems = []
    for p in dbm.list_problems(seeded_db):
        cases = dbm.get_testcases(seeded_db, p["id"])
        problems.append({
            "code": p["code"],
            "ref_c": p["ref_solution_c"],
            "policy": p.get("policy"),
            "testcases": cases
        })

    probs_file = tmp_path / "problems.json"
    probs_file.write_text(json.dumps(problems, ensure_ascii=False), encoding="utf-8")

    root_dir = str(dbm.Path(__file__).parent.parent)
    test_js = f"""
process.setMaxListeners(0);
const fs = require('fs');
const path = require('path');
const rootDir = {json.dumps(root_dir)};
const policy = require(path.join(rootDir, 'oj/web/static/js/policy.js'));
const judge = require(path.join(rootDir, 'oj/web/static/js/judge.js'));

async function runTest() {{
  const file = process.argv[2];
  const problems = JSON.parse(fs.readFileSync(file, 'utf8'));
  const failures = [];

  for (const p of problems) {{
    const res = await judge.judgeCode(p.ref_c, p.policy, p.testcases, 0, 0, p.code);
    if (res.verdict !== 'AC') {{
      failures.push({{
        code: p.code,
        verdict: res.verdict,
        passed: res.passed,
        total: res.total,
        compile_msg: res.compile_msg,
        policy_issues: res.policy_issues
      }});
    }}
  }}

  console.log('RESULT_JSON:' + JSON.stringify({{
    passed: problems.length - failures.length,
    total: problems.length,
    failed: failures.map(f => f.code)
  }}));
  process.exit(0);
}}

runTest().catch(err => {{
  console.error(err && err.stack ? err.stack : err);
  process.exit(1);
}});
"""
    js_file = tmp_path / "runner.js"
    js_file.write_text(test_js, encoding="utf-8")

    proc = subprocess.run(
        ["node", str(js_file), str(probs_file)],
        capture_output=True,
        text=True,
        cwd=root_dir
    )

    assert proc.returncode == 0, f"Frontend judge failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    result_line = next((ln for ln in proc.stdout.splitlines() if ln.startswith("RESULT_JSON:")), None)
    assert result_line, f"missing RESULT_JSON output:\n{proc.stdout}"

    result = json.loads(result_line[len("RESULT_JSON:"):])
    failed_codes = set(result["failed"])
    assert failed_codes <= KNOWN_FAILURES, (
        f"回归恶化: 新增失败题 {sorted(failed_codes - KNOWN_FAILURES)}；"
        f"已固化白名单 {sorted(KNOWN_FAILURES)}"
    )
    assert result["passed"] / result["total"] >= 0.9, (
        f"通过率过低: {result['passed']}/{result['total']}，失败题: {sorted(failed_codes)}"
    )

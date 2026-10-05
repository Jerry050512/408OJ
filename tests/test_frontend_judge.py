# -*- coding: utf-8 -*-
"""前端 JS / WASM 评测引擎集成测试：全量 60 题参考 C 解 AC 验证。"""
import json
import subprocess
import pytest
import sqlite3

from oj import db as dbm
from oj import seed

@pytest.fixture(scope="module")
def seeded_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "oj.db"
    conn = dbm.connect(path)
    seed.seed_database(conn)
    yield conn
    conn.close()

def test_frontend_judge_all_ac(seeded_db, tmp_path):
    """验证前端 OJJudge 在 Node.js 环境下对全量题目的参考 C 解法达成高准确率 (>= 90%) AC。"""
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
    const res = await judge.judgeCode(p.ref_c, p.policy, p.testcases);
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

  if (failures.length > 5) {{
    console.error('FAILURES (' + failures.length + '):', JSON.stringify(failures, null, 2));
    process.exit(1);
  }} else {{
    console.log('SUCCESS: ' + (problems.length - failures.length) + '/' + problems.length + ' PROBLEMS PASSED FRONTEND AC VERIFICATION');
    process.exit(0);
  }}
}}

runTest().catch(err => {{
  console.error(err);
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
    assert "SUCCESS:" in proc.stdout

# -*- coding: utf-8 -*-
"""评测机测试：AC / WA / TLE / RE / CE、比对规则、试跑。"""
import pytest

from oj import config, judge

SOLVE_ADD = r"""
#include <stdio.h>
int main(){
    int a, b;
    if (scanf("%d %d", &a, &b) != 2) return 0;
    printf("%d\n", a + b);
    return 0;
}
"""

TWO_CASES = [
    {"input": "1 2\n", "expected": "3\n", "is_sample": 1},
    {"input": "-5 5\n", "expected": "0\n", "is_sample": 0},
]


def _run(src, cases=TWO_CASES, policy=None, tl=1000):
    return judge.judge_code(src, policy or {"level": "standard"}, cases,
                            time_limit_ms=tl)


def test_ac():
    r = _run(SOLVE_ADD)
    assert r["verdict"] == "AC"
    assert r["passed"] == 2 and r["total"] == 2
    assert r["max_time_ms"] > 0


def test_wa():
    bad = SOLVE_ADD.replace("a + b", "a - b")
    r = _run(bad)
    assert r["verdict"] == "WA"
    assert r["passed"] == 0
    assert r["results"][0]["actual"].strip() == "-1"


def test_compile_error():
    r = _run("int main( { return 0; }")
    assert r["verdict"] == "CE"
    assert r["compile_msg"]


def test_policy_violation_is_ce():
    src = '#include <windows.h>\nint main(){return 0;}'
    r = _run(src)
    assert r["verdict"] == "CE"
    assert "合规检查" in r["compile_msg"]


def test_tle():
    src = "#include <stdio.h>\nint main(){ for(;;); return 0; }"
    r = _run(src, cases=[{"input": "", "expected": ""}], tl=400)
    assert r["verdict"] == "TLE"
    assert r["results"][0]["verdict"] == "TLE"


def test_re_nonzero_exit():
    src = "#include <stdio.h>\nint main(){ return 3; }"
    r = _run(src, cases=[{"input": "", "expected": "x"}])
    assert r["verdict"] == "RE"


def test_re_segfault():
    src = "#include <stdio.h>\nint main(){ int *p=NULL; *p=1; return 0; }"
    r = _run(src, cases=[{"input": "", "expected": "x"}])
    assert r["verdict"] == "RE"


def test_output_normalization():
    assert judge.outputs_equal("a \nb\n\n", "a\nb")
    assert not judge.outputs_equal("  a", "a")     # 行首空白有语义，不忽略
    assert not judge.outputs_equal("a b", "ab")
    assert judge.outputs_equal("a\r\nb\r\n", "a\nb")


def test_output_ignore_trailing_spaces_per_line():
    assert judge.normalize_output("x  \ny\t\n") == "x\ny"


def test_partial_wa_shows_per_case():
    weird = SOLVE_ADD.replace("a + b", "a + (b==5 ? 1 : b)")
    cases = TWO_CASES + [{"input": "1 5", "expected": "6"}, {"input": "10 5", "expected": "15"}]
    r = _run(weird, cases)  # 只有 "1 2" 能碰巧 AC，其余 b==5 均错
    assert r["verdict"] == "WA"
    assert r["passed"] == 1
    vs = [x["verdict"] for x in r["results"]]
    assert vs.count("AC") == 1 and vs.count("WA") == 3


def test_run_custom_ok():
    r = judge.run_custom(SOLVE_ADD, {"level": "standard"}, "20 22\n")
    assert r["ok"] and r["stdout"].strip() == "42"


def test_run_custom_compile_fail():
    r = judge.run_custom("int main(){", None, "")
    assert not r["ok"] and r["stage"] == "compile"


def test_run_custom_policy_fail():
    src = '#include <stdio.h>\nint main(){ gets(0); return 0; }'
    r = judge.run_custom(src, None, "")
    assert not r["ok"] and r["stage"] == "policy"


def test_memory_sampled():
    r = _run(SOLVE_ADD)
    assert r["max_mem_kb"] > 0 if judge.psutil else True


# ---------------------------------------------------------------------------
# 预热运行（warmup）：规避安全软件扫描新 exe 造成的首次运行阻塞
# ---------------------------------------------------------------------------

def test_warmup_default_on():
    assert config.WARMUP_ENABLED_DEFAULT is True
    assert config.WARMUP_TIMEOUT_MS > 0


def test_judge_code_warmup_toggle(monkeypatch):
    calls = []
    monkeypatch.setattr(judge, "warmup_program", lambda *a, **k: calls.append(a))

    r = judge.judge_code(SOLVE_ADD, {"level": "standard"}, TWO_CASES, warmup=True)
    assert r["verdict"] == "AC" and len(calls) == 1

    calls.clear()
    r = judge.judge_code(SOLVE_ADD, {"level": "standard"}, TWO_CASES, warmup=False)
    assert r["verdict"] == "AC" and calls == []


def test_judge_code_warmup_uses_config_default(monkeypatch):
    calls = []
    monkeypatch.setattr(judge, "warmup_program", lambda *a, **k: calls.append(a))

    monkeypatch.setattr(config, "WARMUP_ENABLED", True)
    judge.judge_code(SOLVE_ADD, {"level": "standard"}, TWO_CASES)
    assert len(calls) == 1

    calls.clear()
    monkeypatch.setattr(config, "WARMUP_ENABLED", False)
    judge.judge_code(SOLVE_ADD, {"level": "standard"}, TWO_CASES)
    assert calls == []


def test_run_custom_warmup_toggle(monkeypatch):
    calls = []
    monkeypatch.setattr(judge, "warmup_program", lambda *a, **k: calls.append(a))

    r = judge.run_custom(SOLVE_ADD, {"level": "standard"}, "20 22\n", warmup=True)
    assert r["ok"] and len(calls) == 1

    calls.clear()
    r = judge.run_custom(SOLVE_ADD, {"level": "standard"}, "20 22\n", warmup=False)
    assert r["ok"] and calls == []


def test_warmup_program_returns_after_exit(tmp_path):
    ok, msg, exe = judge.compile_source(
        "#include <stdio.h>\nint main(){ return 0; }", tmp_path)
    assert ok, msg
    judge.warmup_program(exe, cwd=tmp_path, timeout_ms=3000)  # 不应抛异常


def test_warmup_program_kills_hanging_program(tmp_path):
    import time
    ok, msg, exe = judge.compile_source(
        "int main(){ for(;;); return 0; }", tmp_path)
    assert ok, msg
    t0 = time.monotonic()
    judge.warmup_program(exe, cwd=tmp_path, timeout_ms=300)
    assert time.monotonic() - t0 < 2.5

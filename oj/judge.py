"""评测机：GCC 编译 -> 逐测试点运行 -> 比对输出。

- 超时/内存通过轮询 Popen + psutil 实现（psutil 缺失时仅做超时控制）。
- 比对规则：忽略行尾空白与文末空行（标准 OJ 规则）。
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from . import config

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None

EXE_SUFFIX = ".exe" if sys.platform.startswith("win") else ""

VERDICT_AC, VERDICT_WA, VERDICT_TLE = "AC", "WA", "TLE"
VERDICT_RE, VERDICT_CE, VERDICT_SE = "RE", "CE", "SE"


class JudgeError(Exception):
    pass


def find_gcc() -> str:
    gcc = shutil.which("gcc")
    if not gcc:
        raise JudgeError("未找到 gcc，请安装 MinGW/GCC 并加入 PATH")
    return gcc


def compile_source(src: str, workdir: Path) -> tuple[bool, str, Path]:
    """编译 C 源码。返回 (成功, 编译输出, 可执行文件路径)。"""
    workdir.mkdir(parents=True, exist_ok=True)
    src_path = workdir / "main.c"
    exe_path = workdir / ("prog" + EXE_SUFFIX)
    src_path.write_text(src, encoding="utf-8")
    cmd = [find_gcc(), *config.GCC_FLAGS, str(src_path), "-o", str(exe_path), "-lm"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=config.COMPILE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return False, "编译超时", exe_path
    msg = (proc.stderr or "").strip()
    if proc.returncode != 0:
        return False, msg, exe_path
    return True, msg, exe_path


def _sample_memory(proc, proc_psutil) -> int:
    """返回进程树当前 RSS 总和（KB），失败返回 0。"""
    if psutil is None or proc_psutil is None:
        return 0
    try:
        total = proc_psutil.memory_info().rss
        for child in proc_psutil.children(recursive=True):
            try:
                total += child.memory_info().rss
            except psutil.NoSuchProcess:
                pass
        return total // 1024
    except psutil.NoSuchProcess:
        return 0


def run_program(exe_path: Path, stdin_data: str, time_limit_ms: int,
                memory_limit_kb: int, cwd: Path | None = None) -> dict:
    """运行程序一次。返回 {verdict, time_ms, mem_kb, stdout, returncode}。"""
    p_proc = None
    toc = time.monotonic
    t0 = toc()
    peak_kb = 0
    workdir = cwd or exe_path.parent
    # stdout/stderr 重定向到临时文件：避免大输出时管道缓冲满造成子进程阻塞
    out_path = Path(workdir) / "stdout.tmp"
    err_path = Path(workdir) / "stderr.tmp"
    try:
        f_out = open(out_path, "w", encoding="utf-8", errors="replace")
        f_err = open(err_path, "w", encoding="utf-8", errors="replace")
    except OSError as e:
        return {"verdict": VERDICT_SE, "time_ms": 0, "mem_kb": 0,
                "stdout": "", "stderr": str(e), "returncode": None}
    try:
        proc = subprocess.Popen(
            [str(exe_path)], stdin=subprocess.PIPE, stdout=f_out,
            stderr=f_err, cwd=workdir, text=True,
            encoding="utf-8", errors="replace",
        )
    except OSError as e:
        f_out.close(); f_err.close()
        return {"verdict": VERDICT_SE, "time_ms": 0, "mem_kb": 0,
                "stdout": "", "stderr": str(e), "returncode": None}
    if psutil is not None:
        try:
            p_proc = psutil.Process(proc.pid)
        except psutil.NoSuchProcess:
            p_proc = None

    # 喂输入（先写后关，避免大数据 write 阻塞：简单程序输入量小，直接写可行；
    # 用线程更稳，这里采用 communicate 不可行因为要轮询 -> 用 stdin 写入器线程）
    import threading

    def _feed():
        try:
            if stdin_data:
                proc.stdin.write(stdin_data)
            proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass

    feeder = threading.Thread(target=_feed, daemon=True)
    feeder.start()

    verdict = None
    limit_s = time_limit_ms / 1000.0
    while True:
        ret = proc.poll()
        peak_kb = max(peak_kb, _sample_memory(proc, p_proc))
        if ret is not None:
            break
        if toc() - t0 > limit_s:
            verdict = VERDICT_TLE
            proc.kill()
            break
        if memory_limit_kb and peak_kb > memory_limit_kb:
            verdict = "MLE"
            proc.kill()
            break
        time.sleep(0.004)

    time_ms = (toc() - t0) * 1000
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        verdict = verdict or VERDICT_SE
    f_out.close(); f_err.close()
    try:
        stdout = out_path.read_text(encoding="utf-8", errors="replace")
        stderr = err_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        stdout, stderr = "", ""
    if verdict is None:
        if proc.returncode != 0:
            verdict = VERDICT_RE
        else:
            verdict = VERDICT_AC
    return {"verdict": verdict, "time_ms": time_ms, "mem_kb": peak_kb,
            "stdout": stdout, "stderr": stderr, "returncode": proc.returncode}


def warmup_program(exe_path: Path, cwd: Path | None = None,
                   timeout_ms: int | None = None) -> None:
    """预热运行：正式评测前先空跑一次编译产物，并丢弃结果。

    Windows 上的杀毒 / 主动防御软件（如火绒 HipsDaemon）会在刚创建的可执行
    文件首次运行前对其扫描，期间进程被阻塞、CPU 占用为 0，这段等待常达
    1~2 秒。若直接计入第一个测试点会误判为 TLE。这里用空输入跑一次，让安全
    软件完成扫描；超过 timeout_ms 仍未退出则强制结束。
    """
    if timeout_ms is None:
        timeout_ms = config.WARMUP_TIMEOUT_MS
    if timeout_ms <= 0:
        return
    workdir = cwd or exe_path.parent
    try:
        proc = subprocess.Popen(
            [str(exe_path)], stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            cwd=workdir,
        )
    except OSError:
        return
    try:
        proc.wait(timeout=timeout_ms / 1000.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass


def normalize_output(s: str) -> str:
    """OJ 标准比对：去行尾空白、去文末空行，统一换行符。"""
    lines = s.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [ln.rstrip() for ln in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def outputs_equal(expected: str, actual: str) -> bool:
    return normalize_output(expected) == normalize_output(actual)


def judge_code(src: str, policy: dict | None, testcases: list[dict[str, Any]],
               time_limit_ms: int = config.DEFAULT_TIME_LIMIT_MS,
               memory_limit_kb: int = config.DEFAULT_MEMORY_LIMIT_KB,
               keep_build: bool = False,
               warmup: bool | None = None) -> dict:
    """完整评测：policy 检查 + 编译 + 运行所有测试点。

    warmup 为 None 时取 config.WARMUP_ENABLED；正式计时前先空跑一次编译产物，
    避免安全软件扫描新可执行文件造成的首次运行阻塞被判成 TLE。

    返回 dict(verdict, passed, total, compile_msg, results[], max_time_ms, max_mem_kb, policy_issues)
    """
    from .policy import check_source

    issues = check_source(src, policy or {})
    issue_msgs = [i.fmt() for i in issues]
    total = len(testcases)
    base = {"verdict": None, "passed": 0, "total": total, "compile_msg": "",
            "results": [], "max_time_ms": 0.0, "max_mem_kb": 0.0,
            "policy_issues": issue_msgs}
    if issues:
        base["verdict"] = VERDICT_CE
        base["compile_msg"] = "408 合规检查未通过：\n" + "\n".join(issue_msgs)
        return base

    config.BUILD_DIR.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="j", dir=config.BUILD_DIR))
    try:
        ok, cmsg, exe = compile_source(src, workdir)
        base["compile_msg"] = cmsg
        if not ok:
            base["verdict"] = VERDICT_CE
            return base
        do_warmup = config.WARMUP_ENABLED if warmup is None else warmup
        if do_warmup:
            warmup_program(exe, cwd=workdir)
        results = []
        passed = 0
        for idx, tc in enumerate(testcases):
            r = run_program(exe, tc["input"], time_limit_ms, memory_limit_kb, cwd=workdir)
            base["max_time_ms"] = max(base["max_time_ms"], r["time_ms"])
            base["max_mem_kb"] = max(base["max_mem_kb"], r["mem_kb"])
            v = r["verdict"]
            if v == VERDICT_AC and not outputs_equal(tc["expected"], r["stdout"]):
                v = VERDICT_WA
            if v == VERDICT_AC:
                passed += 1
            results.append({
                "ord": idx, "verdict": v, "time_ms": round(r["time_ms"], 1),
                "mem_kb": r["mem_kb"],
                "input": tc["input"][:300], "expected": tc["expected"][:300],
                "actual": r["stdout"][:300],
                "is_sample": tc.get("is_sample", 0),
            })
            if v in (VERDICT_TLE, VERDICT_RE):
                # TLE/RE 耗时或可能挂起，命中的测试点即终止评测（该点评为最终状态）
                break
        base["results"] = results
        base["passed"] = passed
        if passed == total and total > 0:
            base["verdict"] = VERDICT_AC
        elif results and results[-1]["verdict"] in (VERDICT_TLE, VERDICT_RE, "MLE"):
            base["verdict"] = results[-1]["verdict"]
        elif total == 0:
            base["verdict"] = VERDICT_SE
            base["compile_msg"] += "\n题目缺少测试点"
        else:
            base["verdict"] = VERDICT_WA
        return base
    finally:
        if not keep_build:
            shutil.rmtree(workdir, ignore_errors=True)


def run_custom(src: str, policy: dict | None, stdin_data: str,
               time_limit_ms: int = config.DEFAULT_TIME_LIMIT_MS,
               memory_limit_kb: int = config.DEFAULT_MEMORY_LIMIT_KB,
               warmup: bool | None = None) -> dict:
    """试跑：编译并用自定义输入运行一次，返回标准输出。

    warmup 为 None 时取 config.WARMUP_ENABLED。
    """
    from .policy import check_source

    issues = check_source(src, policy or {})
    if issues:
        return {"ok": False, "stage": "policy",
                "message": "408 合规检查未通过：\n" + "\n".join(i.fmt() for i in issues)}
    config.BUILD_DIR.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="r", dir=config.BUILD_DIR))
    try:
        ok, cmsg, exe = compile_source(src, workdir)
        if not ok:
            return {"ok": False, "stage": "compile", "message": cmsg}
        do_warmup = config.WARMUP_ENABLED if warmup is None else warmup
        if do_warmup:
            warmup_program(exe, cwd=workdir)
        r = run_program(exe, stdin_data, time_limit_ms, memory_limit_kb, cwd=workdir)
        return {"ok": r["verdict"] == VERDICT_AC, "stage": "run",
                "verdict": r["verdict"], "stdout": r["stdout"],
                "stderr": r["stderr"][-2000:], "time_ms": round(r["time_ms"], 1),
                "mem_kb": r["mem_kb"], "compile_warnings": cmsg}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

"""408OJ 全局配置。"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("OJ_DATA_DIR", BASE_DIR / "data"))
DB_PATH = Path(os.environ.get("OJ_DB_PATH", DATA_DIR / "oj.db"))
BUILD_DIR = Path(os.environ.get("OJ_BUILD_DIR", BASE_DIR / ".judge_tmp"))

DEFAULT_TIME_LIMIT_MS = 1000
DEFAULT_MEMORY_LIMIT_KB = 64 * 1024

# 预热运行：编译产物在 Windows 上首次执行时，可能被杀毒/主动防御软件
# （如火绒 HipsDaemon）扫描阻塞 1~2 秒。评测正式计时前先空跑一次，
# 让安全软件完成扫描，避免这段等待被计入第一个测试点的耗时。
WARMUP_ENABLED_DEFAULT = True
WARMUP_ENABLED = WARMUP_ENABLED_DEFAULT
WARMUP_TIMEOUT_MS = 3000          # 单次预热的最长等待（含安全软件扫描时间）

MAX_SOURCE_BYTES = 64 * 1024          # 提交源码大小上限
MAX_CUSTOM_INPUT_BYTES = 16 * 1024    # 自定义试跑输入上限
COMPILE_TIMEOUT_S = 15                # 编译超时
GIT_KEEP_FULL_RESULTS = 20            # 提交详情中最多展示的测试点数

# GCC 编译参数：408 使用 C 语言
GCC_FLAGS = ["-O2", "-std=c11", "-Wall", "-Wextra", "-Wno-unused-variable", "-pipe"]

WEB_TITLE = "408OJ"
VERDICT_NAMES = {
    "AC": "Accepted",
    "WA": "Wrong Answer",
    "TLE": "Time Limit Exceeded",
    "RE": "Runtime Error",
    "CE": "Compile Error",
    "SE": "System Error",
    "PD": "Pending",
}

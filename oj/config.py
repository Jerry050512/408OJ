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

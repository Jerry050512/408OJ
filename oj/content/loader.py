# -*- coding: utf-8 -*-
"""题库加载器：兼容旧格式（Python dict）与新格式（JSON + Python 算法）。

旧格式：oj/content/real_*.py, practice.py 中的 PROBLEMS 列表
新格式：oj/content/data/mock.json + oj/content/alg_mock.py

加载顺序：
1. 旧格式题目（真题 + 练习题）从原有 Python 模块加载
2. 新格式题目（模拟题等）从 JSON + 对应算法模块加载
"""
from __future__ import annotations

import json
from pathlib import Path

from . import real_2012_2016, real_2017_2021, real_2022_2026, practice

# 旧格式模块
_LEGACY_MODULES = [real_2012_2016, real_2017_2021, real_2022_2026, practice]

# 新格式数据目录
_DATA_DIR = Path(__file__).parent / "data"

# 新格式算法模块映射：JSON 文件名 → (算法模块名, 包路径)
_ALG_MAP = {
    "mock.json": ("alg_mock", "oj.content.alg_mock"),
}


def _load_legacy() -> list[dict]:
    """从旧格式 Python 模块加载题目。"""
    out: list[dict] = []
    for mod in _LEGACY_MODULES:
        out.extend(mod.PROBLEMS)
    return out


def _load_new_format() -> list[dict]:
    """从 JSON 数据文件 + Python 算法模块加载题目。"""
    import importlib
    out: list[dict] = []

    for json_name, (alg_attr, alg_pkg) in _ALG_MAP.items():
        json_path = _DATA_DIR / json_name
        if not json_path.exists():
            continue

        with open(json_path, encoding="utf-8") as f:
            data_list = json.load(f)

        # 加载算法模块
        alg_mod = None
        try:
            alg_mod = importlib.import_module(alg_pkg)
        except ImportError:
            pass

        for data in data_list:
            code = data["code"]
            func_name = code.replace("-", "_")

            problem = dict(data)
            if alg_mod is not None:
                gen = getattr(alg_mod, f"gen_{func_name}", None)
                ref_py = getattr(alg_mod, f"ref_{func_name}", None)
                if gen is not None:
                    problem["gen"] = gen
                if ref_py is not None:
                    problem["ref_py"] = ref_py

            # 默认值
            problem.setdefault("samples", [])
            problem.setdefault("time_limit_ms", 1000)
            problem.setdefault("memory_limit_kb", 64 * 1024)
            problem.setdefault("policy", {"level": "standard"})
            problem.setdefault("lang_hint", "")
            problem.setdefault("solution_md", "")
            problem.setdefault("ref_c", "")
            problem.setdefault("year", None)
            problem.setdefault("exam_no", "")

            out.append(problem)

    return out


def all_problem_defs() -> list[dict]:
    """加载全部题目定义。"""
    return _load_legacy() + _load_new_format()

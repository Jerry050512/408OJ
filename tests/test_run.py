# -*- coding: utf-8 -*-
"""run.py 命令行参数测试：--no-warmup 开关。"""
import importlib.util
import sys
from pathlib import Path

from oj import config

RUN_PY = Path(__file__).resolve().parent.parent / "run.py"


def _load_run_module():
    spec = importlib.util.spec_from_file_location("oj_run_entry", RUN_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _stub_server(monkeypatch):
    """让 run.main() 不真正启动 uvicorn / 建库。"""
    import uvicorn
    import oj.web.app as app_mod
    ran = {}

    def fake_run(*a, **k):
        ran["yes"] = True

    monkeypatch.setattr(uvicorn, "run", fake_run)
    monkeypatch.setattr(app_mod, "create_app", lambda *a, **k: None)
    return ran


def test_no_warmup_flag_disables(monkeypatch):
    run = _load_run_module()
    ran = _stub_server(monkeypatch)
    config.WARMUP_ENABLED = True  # 模拟默认开启
    monkeypatch.setattr(sys, "argv", ["run.py", "--no-warmup", "--db", ":memory:"])
    run.main()
    assert config.WARMUP_ENABLED is False
    assert ran.get("yes")


def test_default_keeps_warmup_enabled(monkeypatch):
    run = _load_run_module()
    ran = _stub_server(monkeypatch)
    config.WARMUP_ENABLED = True  # 模拟默认开启
    monkeypatch.setattr(sys, "argv", ["run.py", "--db", ":memory:"])
    run.main()
    assert config.WARMUP_ENABLED is True
    assert ran.get("yes")

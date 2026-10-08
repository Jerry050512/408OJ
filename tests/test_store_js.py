# -*- coding: utf-8 -*-
"""通过 node 运行 store.js 的行为测试（配额超限保护 / 提交纪录剪裁 / 草稿兼容性）。"""
import shutil
import subprocess
from pathlib import Path

import pytest

NODE = shutil.which("node")
TEST_FILE = Path(__file__).parent / "store_js.test.js"


@pytest.mark.skipif(NODE is None, reason="node 不可用")
def test_store_js_behaviors():
    r = subprocess.run([NODE, str(TEST_FILE)], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    assert "ALL store.js tests passed!" in r.stdout

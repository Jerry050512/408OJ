# -*- coding: utf-8 -*-
"""通过 node 运行 editor.js 的行为测试（回车缩进 / 语法高亮）。"""
import shutil
import subprocess
from pathlib import Path

import pytest

NODE = shutil.which("node")
TEST_FILE = Path(__file__).parent / "editor_js.test.js"


@pytest.mark.skipif(NODE is None, reason="node 不可用")
def test_editor_js_behaviors():
    r = subprocess.run([NODE, str(TEST_FILE)], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_editor_js_selfcontained():
    """编辑器脚本必须离线自包含（不依赖任何 CDN）。"""
    src = Path(__file__).parent.parent / "oj/web/static/js/editor.js"
    text = src.read_text(encoding="utf-8")
    assert "http://" not in text and "https://" not in text
    assert "require(" not in text.split("module.exports")[0]  # 无运行时依赖

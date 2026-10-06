# -*- coding: utf-8 -*-
"""通过 node 运行 editor.js 的行为测试（回车缩进 / 语法高亮）及静态模式校验。"""
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


def test_static_dist_html_configuration():
    """验证生成的静态 dist HTML 页面中 window.STATIC_MODE = true 已正确配置。"""
    from build_static import build_static_site
    build_static_site()

    dist_dir = Path(__file__).parent.parent / "dist"
    index_html = dist_dir / "index.html"
    problem_html = dist_dir / "p" / "real-2012-41" / "index.html"

    assert index_html.exists()
    assert problem_html.exists()

    p_content = problem_html.read_text(encoding="utf-8")
    assert "window.STATIC_MODE = true;" in p_content
    assert "/static/js/picoc.umd.js" in p_content
    assert "/static/js/judge.js" in p_content

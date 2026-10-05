# -*- coding: utf-8 -*-
"""Markdown 渲染公共模块。

对代码块外的 #include <xxx> 做实体预转义，防止 Markdown 渲染后
尖括号被浏览器解析为未知 HTML 标签导致头文件名丢失。
"""
from __future__ import annotations

import re

import markdown


def md(text: str) -> str:
    if not text:
        return ""
    blocks = []

    def stash(m):
        blocks.append(m.group(0))
        return "\x02%d\x03" % (len(blocks) - 1)

    text = re.sub(r"```.*?```|~~~.*?~~~|`[^`\n]*`", stash, text, flags=re.S)
    text = re.sub(r"#include\s*<([^>]+)>", r"#include &lt;\1&gt;", text)
    text = re.sub(r"<([A-Za-z0-9_]+\.[A-Za-z0-9_]+)>", r"&lt;\1&gt;", text)
    for i, b in enumerate(blocks):
        text = text.replace("\x02%d\x03" % i, b)
    return markdown.markdown(text, extensions=["fenced_code", "tables", "nl2br"])

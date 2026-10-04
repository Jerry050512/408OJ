"""408 源代码合规静态检查。

模拟 408 考场对 C 语言的约束：
- 头文件白名单（standard / strict 两级，strict 对应王道"只用 stdio/stdlib"标准）；
- 禁用函数黑名单（文件、进程、系统、网络等绝不属于考试范围的调用）；
- 提交前即可拦截，违规记为 CE(policy)。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# standard: 408 考试常用基础库
STANDARD_HEADERS = {
    "stdio.h", "stdlib.h", "string.h", "ctype.h", "math.h",
    "limits.h", "stddef.h", "stdbool.h", "float.h",
}
# strict: 王道严格标准（手撕字符串/字符处理，不给 string.h / ctype.h / math.h）
STRICT_HEADERS = {
    "stdio.h", "stdlib.h", "limits.h", "stddef.h", "stdbool.h", "float.h",
}

# 任何级别都禁止的标识符（文件 / 进程 / 系统 / 网络 / 线程 / 寄存器跳转 等）
BANNED_IDENTIFIERS: dict[str, str] = {
    "system": "禁止调用系统命令",
    "popen": "禁止创建管道进程", "pclose": "禁止创建管道进程",
    "fopen": "禁止文件 I/O", "freopen": "禁止文件 I/O（本地评测请用标准输入）",
    "fclose": "禁止文件 I/O", "remove": "禁止文件操作", "rename": "禁止文件操作",
    "tmpfile": "禁止文件操作", "tmpnam": "禁止文件操作",
    "execve": "禁止创建进程", "execl": "禁止创建进程", "execle": "禁止创建进程",
    "execlp": "禁止创建进程", "execv": "禁止创建进程", "execvp": "禁止创建进程",
    "fork": "禁止创建进程",
    "exit": None,  # exit 允许；占位于说明
    "abort": "请用 return 结束程序",
    "signal": "超出 408 范围",
    "setjmp": "超出 408 范围", "longjmp": "超出 408 范围",
    "gets": "gets 已移出 C 标准且不安全，请使用 scanf / fgets",
    "asm": "禁止内联汇编",
    "socket": "禁止网络编程",
    "Sleep": "超出 408 范围", "sleep": "超出 408 范围",
    "pthread_create": "禁止多线程",
    "CreateThread": "禁止多线程", "CreateProcess": "禁止创建进程",
    "time": None,  # 时间函数不属于考试范围，但无害；严格模式下禁止
    "rand": None,
}

# strict 级别下额外禁止（考场上应手写等价逻辑）
STRICT_EXTRA_BANNED: dict[str, str] = {
    "strlen": "strict 模式：请手写循环求长度", "strcpy": "strict 模式：请手写字符复制",
    "strncpy": "strict 模式：请手写字符复制", "strcmp": "strict 模式：请手写字符比较",
    "strncmp": "strict 模式：请手写字符比较", "strcat": "strict 模式：请手写字符拼接",
    "strchr": "strict 模式：请手写查找", "strstr": "strict 模式：请手写查找",
    "memset": "strict 模式：请手写初始化", "memcpy": "strict 模式：请手写复制",
    "memmove": "strict 模式", "memchr": "strict 模式",
    "isalpha": "strict 模式：请手写判断", "isdigit": "strict 模式：请手写判断",
    "isspace": "strict 模式：请手写判断", "toupper": "strict 模式", "tolower": "strict 模式",
    "sqrt": "strict 模式", "pow": "strict 模式", "fabs": "strict 模式",
    "qsort": "408 考试要求手写排序", "bsearch": "408 考试要求手写查找",
}

# standard 模式同样禁止的"拿来主义"算法库函数（408 大题要求手写排序/查找）
STANDARD_BANNED_CALLS: dict[str, str] = {
    "qsort": "408 考试要求手写排序，禁止使用 qsort",
    "bsearch": "408 考试要求手写查找，禁止使用 bsearch",
}


@dataclass
class Issue:
    level: str      # "error"
    kind: str       # header / identifier / directive
    name: str
    message: str
    line: int

    def fmt(self) -> str:
        return f"第 {self.line} 行: [{self.kind}] {self.name} — {self.message}"


def strip_comments_and_literals(src: str) -> str:
    """去掉注释与字符串/字符字面量（保留换行以便行号对齐）。"""
    out = []
    i, n = 0, len(src)
    state = "code"  # code | line_comment | block_comment | str | chr
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if state == "code":
            if c == "/" and nxt == "/":
                state = "line_comment"; out.append("  "); i += 2
            elif c == "/" and nxt == "*":
                state = "block_comment"; out.append("  "); i += 2
            elif c == '"':
                state = "str"; out.append('""'); i += 1
            elif c == "'":
                state = "chr"; out.append("''"); i += 1
            else:
                out.append(c); i += 1
        elif state == "line_comment":
            if c == "\n":
                state = "code"; out.append("\n")
            else:
                out.append(" ")
            i += 1
        elif state == "block_comment":
            if c == "*" and nxt == "/":
                state = "code"; out.append("  "); i += 2
            else:
                out.append("\n" if c == "\n" else " "); i += 1
        elif state == "str":
            if c == "\\":
                out.append("  "); i += 2
            elif c == '"':
                state = "code"; out.append('"'); i += 1
            else:
                out.append("\n" if c == "\n" else " "); i += 1
        elif state == "chr":
            if c == "\\":
                out.append("  "); i += 2
            elif c == "'":
                state = "code"; out.append("'"); i += 1
            else:
                out.append("\n" if c == "\n" else " "); i += 1
    return "".join(out)


def check_source(src: str, policy: dict | None = None) -> list[Issue]:
    """对 C 源码做 408 合规检查，返回违规列表（空 = 通过）。"""
    policy = policy or {}
    level = policy.get("level", "standard")
    allowed = set(STRICT_HEADERS if level == "strict" else STANDARD_HEADERS)
    allowed.update(policy.get("extra_allow", []))
    banned_calls: dict[str, str] = dict(STANDARD_BANNED_CALLS)
    if level == "strict":
        banned_calls.update(STRICT_EXTRA_BANNED)

    clean = strip_comments_and_literals(src)
    issues: list[Issue] = []
    seen: set[tuple] = set()

    # 1) #include 检查（逐行，捕获真实头文件名；同时拦截绝对路径/可疑 include）
    for lineno, line in enumerate(clean.splitlines(), 1):
        m = re.match(r"\s*#\s*include\s*(.*)", line)
        if not m:
            continue
        target = m.group(1).strip()
        hm = re.match(r'[<"]([A-Za-z0-9_./\\-]+)[>"]', target)
        if not hm:
            issues.append(Issue("error", "header", "#include",
                                "非法的头文件引入形式", lineno))
            continue
        name = hm.group(1)
        if "/" in name or "\\" in name or ":" in name:
            issues.append(Issue("error", "header", name,
                                "禁止引入自定义路径头文件，408 仅允许标准库", lineno))
        elif name.lower() not in allowed:
            lvl = "strict" if level == "strict" else "standard"
            issues.append(Issue("error", "header", name,
                                f"不在 408 {lvl} 白名单内（允许: "
                                f"{', '.join(sorted(allowed))}）", lineno))

    # 2) 禁用标识符（词边界匹配函数调用形式 name( ）
    id_pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    for lineno, line in enumerate(clean.splitlines(), 1):
        for m in id_pattern.finditer(line):
            name = m.group(1)
            reason = None
            kind = "identifier"
            if name in BANNED_IDENTIFIERS and BANNED_IDENTIFIERS[name]:
                reason = BANNED_IDENTIFIERS[name]
            elif name in banned_calls:
                reason = banned_calls[name]
            if reason and (kind, name) not in seen:
                seen.add((kind, name))
                issues.append(Issue("error", "identifier", name, reason, lineno))
    issues.sort(key=lambda i: i.line)
    return issues

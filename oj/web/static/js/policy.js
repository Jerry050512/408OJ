/* 408 源代码合规静态检查 (JS 版)。
 * 模拟 408 考场对 C 语言的约束：头文件白名单、禁用函数黑名单。
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.OJPolicy = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const STANDARD_HEADERS = new Set([
    "stdio.h", "stdlib.h", "string.h", "ctype.h", "math.h",
    "limits.h", "stddef.h", "stdbool.h", "float.h",
  ]);

  const STRICT_HEADERS = new Set([
    "stdio.h", "stdlib.h", "limits.h", "stddef.h", "stdbool.h", "float.h",
  ]);

  const BANNED_IDENTIFIERS = {
    "system": "禁止调用系统命令",
    "popen": "禁止创建管道进程", "pclose": "禁止创建管道进程",
    "fopen": "禁止文件 I/O", "freopen": "禁止文件 I/O（本地评测请用标准输入）",
    "fclose": "禁止文件 I/O", "remove": "禁止文件操作", "rename": "禁止文件操作",
    "tmpfile": "禁止文件操作", "tmpnam": "禁止文件操作",
    "execve": "禁止创建进程", "execl": "禁止创建进程", "execle": "禁止创建进程",
    "execlp": "禁止创建进程", "execv": "禁止创建进程", "execvp": "禁止创建进程",
    "fork": "禁止创建进程",
    "abort": "请用 return 结束程序",
    "signal": "超出 408 范围",
    "setjmp": "超出 408 范围", "longjmp": "超出 408 范围",
    "gets": "gets 已移出 C 标准且不安全，请使用 scanf / fgets",
    "asm": "禁止内联汇编",
    "socket": "禁止网络编程",
    "Sleep": "超出 408 范围", "sleep": "超出 408 范围",
    "pthread_create": "禁止多线程",
    "CreateThread": "禁止多线程", "CreateProcess": "禁止创建进程",
  };

  const STRICT_EXTRA_BANNED = {
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
  };

  const STANDARD_BANNED_CALLS = {
    "qsort": "408 考试要求手写排序，禁止使用 qsort",
    "bsearch": "408 考试要求手写查找，禁止使用 bsearch",
  };

  function stripCommentsAndLiterals(src) {
    const out = [];
    let i = 0, n = src.length;
    let state = "code";
    while (i < n) {
      const c = src[i];
      const nxt = i + 1 < n ? src[i + 1] : "";
      if (state === "code") {
        if (c === "/" && nxt === "/") {
          state = "line_comment"; out.push("  "); i += 2;
        } else if (c === "/" && nxt === "*") {
          state = "block_comment"; out.push("  "); i += 2;
        } else if (c === '"') {
          state = "str"; out.push('""'); i += 1;
        } else if (c === "'") {
          state = "chr"; out.push("''"); i += 1;
        } else {
          out.push(c); i += 1;
        }
      } else if (state === "line_comment") {
        if (c === "\n") {
          state = "code"; out.push("\n");
        } else {
          out.push(" ");
        }
        i += 1;
      } else if (state === "block_comment") {
        if (c === "*" && nxt === "/") {
          state = "code"; out.push("  "); i += 2;
        } else {
          out.push(c === "\n" ? "\n" : " "); i += 1;
        }
      } else if (state === "str") {
        if (c === "\\") {
          out.push("  "); i += 2;
        } else if (c === '"') {
          state = "code"; out.push('"'); i += 1;
        } else {
          out.push(c === "\n" ? "\n" : " "); i += 1;
        }
      } else if (state === "chr") {
        if (c === "\\") {
          out.push("  "); i += 2;
        } else if (c === "'") {
          state = "code"; out.push("'"); i += 1;
        } else {
          out.push(c === "\n" ? "\n" : " "); i += 1;
        }
      }
    }
    return out.join("");
  }

  function checkSource(src, policy) {
    policy = policy || {};
    const level = policy.level || "standard";
    const allowed = new Set(level === "strict" ? STRICT_HEADERS : STANDARD_HEADERS);
    if (policy.extra_allow) {
      policy.extra_allow.forEach(h => allowed.add(h));
    }

    const bannedCalls = Object.assign({}, STANDARD_BANNED_CALLS);
    if (level === "strict") {
      Object.assign(bannedCalls, STRICT_EXTRA_BANNED);
    }

    const clean = stripCommentsAndLiterals(src);
    const issues = [];
    const seen = new Set();
    const lines = clean.split(/\r?\n/);

    // 1) #include 检查
    lines.forEach((line, idx) => {
      const lineno = idx + 1;
      const m = line.match(/^\s*#\s*include\s*(.*)/);
      if (!m) return;
      const target = m[1].trim();
      const hm = target.match(/^(<([A-Za-z0-9_.\/\\-]+)>|"([A-Za-z0-9_.\/\\-]+)")/);
      if (!hm) {
        issues.push({
          level: "error", kind: "header", name: "#include",
          message: "非法的头文件引入形式", line: lineno,
          fmt: function() { return `第 ${this.line} 行: [${this.kind}] ${this.name} — ${this.message}`; }
        });
        return;
      }
      const name = hm[2] || hm[3];
      if (name.includes("/") || name.includes("\\") || name.includes(":")) {
        issues.push({
          level: "error", kind: "header", name: name,
          message: "禁止引入自定义路径头文件，408 仅允许标准库", line: lineno,
          fmt: function() { return `第 ${this.line} 行: [${this.kind}] ${this.name} — ${this.message}`; }
        });
      } else if (!allowed.has(name.toLowerCase())) {
        const lvl = level === "strict" ? "strict" : "standard";
        const allowedArr = Array.from(allowed).sort().join(", ");
        issues.push({
          level: "error", kind: "header", name: name,
          message: `不在 408 ${lvl} 白名单内（允许: ${allowedArr}）`, line: lineno,
          fmt: function() { return `第 ${this.line} 行: [${this.kind}] ${this.name} — ${this.message}`; }
        });
      }
    });

    // 2) 禁用标识符匹配 name(
    const idPattern = /\b([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
    lines.forEach((line, idx) => {
      const lineno = idx + 1;
      let m;
      idPattern.lastIndex = 0;
      while ((m = idPattern.exec(line)) !== null) {
        const name = m[1];
        let reason = null;
        const kind = "identifier";
        if (BANNED_IDENTIFIERS[name]) {
          reason = BANNED_IDENTIFIERS[name];
        } else if (bannedCalls[name]) {
          reason = bannedCalls[name];
        }
        if (reason && !seen.has(`${kind}:${name}`)) {
          seen.add(`${kind}:${name}`);
          issues.push({
            level: "error", kind: kind, name: name,
            message: reason, line: lineno,
            fmt: function() { return `第 ${this.line} 行: [${this.kind}] ${this.name} — ${this.message}`; }
          });
        }
      }
    });

    issues.sort((a, b) => a.line - b.line);
    return issues;
  }

  return {
    checkSource: checkSource,
    stripCommentsAndLiterals: stripCommentsAndLiterals
  };
}));

/* 408OJ 轻量代码编辑器
 * - textarea 输入层 + <pre> 语法高亮层（原生实现，无依赖离线可用）
 * - 行号槽 / Tab 缩进 / 自动保存草稿到 localStorage
 */
(function () {
  const root = typeof window !== 'undefined' ? window : globalThis;
  const KEYWORDS = new Set([
    'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break',
    'continue', 'return', 'goto', 'sizeof', 'typedef', 'struct', 'union',
    'enum', 'static', 'const', 'extern', 'register', 'volatile', 'inline',
    'restrict', 'auto', 'signed', 'unsigned'
  ]);
  const TYPES = new Set([
    'int', 'char', 'float', 'double', 'long', 'short', 'void', 'bool',
    '_Bool', 'size_t', 'ptrdiff_t', 'FILE', 'true', 'false', 'NULL',
    'int8_t', 'int16_t', 'int32_t', 'int64_t', 'uint32_t', 'uint64_t'
  ]);

  const RE = new RegExp([
    '(\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/)',          // 1 注释
    '("(?:\\\\.|[^"\\\\\\n])*"|\'(?:\\\\.|[^\'\\\\\\n])*\')', // 2 字符串/字符
    '(^|\\n)([ \\t]*#[^\\n]*)',                       // 3 换行前缀 4 预处理
    '\\b(0[xX][0-9a-fA-F]+|\\d+(?:\\.\\d+)?[fFlLuU]*)\\b', // 5 数字
    '\\b([A-Za-z_][A-Za-z0-9_]*)\\b(?=\\s*\\()',      // 6 函数调用
    '\\b([A-Za-z_][A-Za-z0-9_]*)\\b'                  // 7 标识符
  ].join('|'), 'gm');

  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function highlight(src) {
    let out = '';
    let last = 0;
    src.replace(RE, function (m, com, str, nl, pre, num, fn, ident, offset) {
      out += escapeHtml(src.slice(last, offset));
      last = offset + m.length;
      if (com) return out += '<span class="tok-c">' + escapeHtml(com) + '</span>', m;
      if (str) return out += '<span class="tok-s">' + escapeHtml(str) + '</span>', m;
      if (pre) return out += escapeHtml(nl) + '<span class="tok-p">' + escapeHtml(pre) + '</span>', m;
      if (num !== undefined) return out += '<span class="tok-n">' + escapeHtml(num) + '</span>', m;
      if (fn) return out += '<span class="tok-f">' + escapeHtml(fn) + '</span>', m;
      if (ident) {
        if (KEYWORDS.has(ident)) return out += '<span class="tok-k">' + escapeHtml(ident) + '</span>', m;
        if (TYPES.has(ident)) return out += '<span class="tok-t">' + escapeHtml(ident) + '</span>', m;
        return out += escapeHtml(ident), m;
      }
      return m;
    });
    out += escapeHtml(src.slice(last));
    return out + '\n';  // 末行保持高度一致
  }

  let ta, hl, hlScroll, gutter, gutterInner, saveKey, saveTimer;

  // node 环境导出（pytest 通过 node 单测）
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { computeEnter, highlight };
  }

  function render() {
    const src = ta.value;
    hl.innerHTML = highlight(src);
    // 行号
    const lines = src.split('\n').length;
    if (gutterInner.childElementCount !== lines) {
      let html = '';
      for (let i = 1; i <= lines; i++) html += '<span>' + i + '</span>';
      gutterInner.innerHTML = html;
    }
    syncScroll();
    scheduleSave();
  }

  function syncScroll() {
    hlScroll.scrollTop = ta.scrollTop;
    hlScroll.scrollLeft = ta.scrollLeft;
    gutterInner.style.transform = 'translateY(' + (-ta.scrollTop) + 'px)';
  }

  function cleanOldDraftsExcept(preserveKey) {
    if (typeof localStorage === 'undefined') return;
    try {
      const keysToRemove = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && (k.startsWith('oj-code-') || k.startsWith('408oj_draft_'))) {
          if (preserveKey && k === preserveKey) continue;
          keysToRemove.push(k);
        }
      }
      keysToRemove.forEach(k => {
        try { localStorage.removeItem(k); } catch (e) {}
      });
    } catch (e) {}
  }

  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(function () {
      try {
        localStorage.setItem(saveKey, ta.value);
        const el = document.getElementById('saveState');
        if (el) el.textContent = '草稿已保存 ' + new Date().toLocaleTimeString();
      } catch (e) {
        // 存储空间满：清理其他题目的旧草稿并重试
        cleanOldDraftsExcept(saveKey);
        try {
          localStorage.setItem(saveKey, ta.value);
          const el = document.getElementById('saveState');
          if (el) el.textContent = '草稿已保存 ' + new Date().toLocaleTimeString();
        } catch (_) {
          const el = document.getElementById('saveState');
          if (el) el.textContent = '存储空间满，草稿保存失败';
        }
      }
    }, 400);
  }

  // 纯函数：回车时计算插入文本与新光标位置（供浏览器与 node 测试共用）
  function computeEnter(before, after, s) {
    const lineStart = before.lastIndexOf('\n') + 1;
    const curLine = before.slice(lineStart);
    const indent = (curLine.match(/^\s*/) || [''])[0];
    const deeper = /[{]\s*(\/\*[\s\S]*\*\/\s*)?$/.test(curLine) ? '    ' : '';
    const trimmedAfter = after.replace(/^[ \t]*/, '');
    if (deeper && trimmedAfter.startsWith('}')) {
      const first = '\n' + indent + deeper;
      return { insert: first + '\n' + indent, caret: s + first.length };
    }
    const insert = '\n' + indent + deeper;
    return { insert, caret: s + insert.length };
  }

  root.initEditor = function (pcode, hint) {
    ta = document.getElementById('code');
    hl = document.getElementById('hl');
    hlScroll = document.getElementById('hlScroll');
    gutter = document.getElementById('gutter');
    gutterInner = document.getElementById('gutterInner');
    saveKey = 'oj-code-' + pcode;

    let saved = null;
    try { saved = localStorage.getItem(saveKey); } catch (e) { }
    ta.value = saved || (hint || '#include <stdio.h>\n\nint main(void){\n    \n    return 0;\n}\n');

    ta.addEventListener('input', render);
    ta.addEventListener('scroll', syncScroll);
    ta.addEventListener('keydown', function (e) {
      if (e.key === 'Tab') {
        e.preventDefault();
        const s = ta.selectionStart, t = ta.selectionEnd;
        ta.value = ta.value.slice(0, s) + '    ' + ta.value.slice(t);
        ta.selectionStart = ta.selectionEnd = s + 4;
        render();
      } else if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey) {
        // 回车自动缩进：对齐上一行缩进；上一行以 { 开头再进一级；
        // 若光标后紧跟 }（空块），则生成 "{\n    |\n}" 结构并把光标放在中间。
        e.preventDefault();
        const s = ta.selectionStart, t = ta.selectionEnd;
        const before = ta.value.slice(0, s);
        const after = ta.value.slice(t);
        const { insert, caret } = computeEnter(before, after, s);
        ta.value = before + insert + after;
        ta.selectionStart = ta.selectionEnd = caret;
        render();
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const btn = document.getElementById('btnSubmit');
        if (btn) btn.click();
      }
    });
    render();
  };

  // 静态页高亮：题解页参考实现、提交详情页代码、Markdown 里的 ```c 块
  root.highlightCBlocks = function () {
    document.querySelectorAll('#src-view, #refcode, .prose pre code.language-c, .prose pre code.c')
      .forEach(function (el) {
        el.innerHTML = highlight(el.textContent.replace(/\n$/, ''));
      });
  };
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', root.highlightCBlocks);
    } else {
      root.highlightCBlocks();
    }
  }

  root.getCode = function () { return (typeof ta !== 'undefined' && ta) ? ta.value : ''; };
  root.resetCode = function () {
    if (!confirm('确定清空当前代码并重置为骨架？')) return;
    ta.value = '#include <stdio.h>\n#include <stdlib.h>\n\nint main(void){\n    \n    return 0;\n}\n';
    render();
  };
})();

/* 408OJ 轻量代码编辑器
 * - textarea 输入层 + <pre> 语法高亮层（原生实现，无依赖离线可用）
 * - 行号槽 / Tab 缩进 / 自动保存草稿到 localStorage
 */
(function () {
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

  let ta, hl, hlScroll, gutter, saveKey, saveTimer;

  function render() {
    const src = ta.value;
    hl.innerHTML = highlight(src);
    // 行号
    const lines = src.split('\n').length;
    if (gutter.childElementCount !== lines) {
      let html = '';
      for (let i = 1; i <= lines; i++) html += '<span>' + i + '</span>';
      gutter.innerHTML = html;
    }
    syncScroll();
    scheduleSave();
  }

  function syncScroll() {
    hlScroll.scrollTop = ta.scrollTop;
    hlScroll.scrollLeft = ta.scrollLeft;
    gutter.style.transform = 'translateY(' + (-ta.scrollTop) + 'px)';
    gutter.style.height = ta.clientHeight + 'px';
  }

  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(function () {
      try {
        localStorage.setItem(saveKey, ta.value);
        const el = document.getElementById('saveState');
        if (el) el.textContent = '草稿已保存 ' + new Date().toLocaleTimeString();
      } catch (e) { /* 存储满时静默 */ }
    }, 400);
  }

  window.initEditor = function (pcode, hint) {
    ta = document.getElementById('code');
    hl = document.getElementById('hl');
    hlScroll = document.getElementById('hlScroll');
    gutter = document.getElementById('gutter');
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
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const btn = document.getElementById('btnSubmit');
        if (btn) btn.click();
      }
    });
    render();
  };

  window.getCode = function () { return ta ? ta.value : ''; };
  window.resetCode = function () {
    if (!confirm('确定清空当前代码并重置为骨架？')) return;
    ta.value = '#include <stdio.h>\n#include <stdlib.h>\n\nint main(void){\n    \n    return 0;\n}\n';
    render();
  };
})();

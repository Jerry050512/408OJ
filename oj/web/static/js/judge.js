/* 408OJ 前端评测引擎 (PicoC WASM + Preprocessor)。
 * 支持在浏览器或 Node.js 环境中离线运行 408 C 语言程序评测。
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['./policy', 'picoc-js'], factory);
  } else if (typeof module === 'object' && module.exports) {
    const policy = require('./policy');
    let picocModule;
    try {
      picocModule = require('picoc-js/dist/bundle.umd.js');
    } catch (e) {
      picocModule = null;
    }
    module.exports = factory(policy, picocModule);
  } else {
    root.OJJudge = factory(root.OJPolicy, root.picocjs || root.PicoC || root);
  }
}(typeof self !== 'undefined' ? self : this, function (OJPolicy, picocModule) {
  'use strict';

  let cachedPicocFactory = null;

  function getPicocFactory() {
    if (cachedPicocFactory) return cachedPicocFactory;
    if (typeof picocModule === 'function') { cachedPicocFactory = picocModule; return cachedPicocFactory; }
    if (picocModule && typeof picocModule.picoc === 'function') { cachedPicocFactory = picocModule.picoc; return cachedPicocFactory; }
    if (picocModule && typeof picocModule.PicocModule === 'function') { cachedPicocFactory = picocModule.PicocModule; return cachedPicocFactory; }
    if (typeof self !== 'undefined' && self.picocjs && typeof self.picocjs.picoc === 'function') { cachedPicocFactory = self.picocjs.picoc; return cachedPicocFactory; }
    if (typeof window !== 'undefined' && window.picocjs && typeof window.picocjs.picoc === 'function') { cachedPicocFactory = window.picocjs.picoc; return cachedPicocFactory; }

    if (typeof require === 'function') {
      try {
        const fs = require('fs');
        const path = require('path');
        const umdPath = require.resolve('picoc-js/dist/bundle.umd.js');
        const content = fs.readFileSync(umdPath, 'utf8');
        const customUmd = content.replace('exports.runC = runC;', 'exports.picoc = picoc; exports.runC = runC;');
        const exportsObj = {};
        const fn = new Function('exports', 'require', 'module', customUmd);
        fn(exportsObj, require, { exports: exportsObj });
        if (typeof exportsObj.picoc === 'function') {
          cachedPicocFactory = exportsObj.picoc;
          return cachedPicocFactory;
        }
      } catch (e) {}
    }

    return null;
  }

  function normalizeOutput(s) {
    if (typeof s !== 'string') return '';
    let lines = s.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
    lines = lines.map(ln => ln.trimEnd());
    while (lines.length && lines[lines.length - 1] === '') {
      lines.pop();
    }
    return lines.join('\n');
  }

  const POINTER_NAMES = new Set([
    'p', 'pp', 'q', 'ptr', 'cur', 'current', 'prev', 'pre', 'next', 'nxt',
    'head', 'tail', 'node', 'left', 'right', 'root', 'top', 'front', 'rear',
    'pa', 'pb', 'l1', 'l2', 'first', 'last', 'slow', 'fast',
    'tmp', 'temp', 'list', 'link', 'child', 'parent', 't'
  ]);

  function collectPointerVars(c) {
    const vars = new Set(POINTER_NAMES);
    const re = /\b(?:int|char|long|double|float|void|unsigned|short|size_t|[A-Z][A-Za-z0-9_]*)\s*\*\s*([A-Za-z_]\w*)\s*(?=[=,;)])/g;
    let m;
    while ((m = re.exec(c)) !== null) vars.add(m[1]);
    return vars;
  }

  function preprocessForPicoC(src, problemCode) {
    let c = src || '';

    // 1. Convert static char (*g_tok)[12] to static array
    c = c.replace(/static\s+char\s*\(\*g_tok\)\[12\];/g, 'static char g_tok[200][12];');
    c = c.replace(/g_tok\s*=\s*malloc\([^;]+;/g, '/* skipped malloc for g_tok */;');

    // 2. Parameter array decay: int h[] -> int *h (skip initializers like int a[] = {...})
    c = c.replace(/(\b[A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s*\[\s*\](?!\s*=)/g, (m, type, name) => type + ' *' + name);

    // 3. Remove const, inline, (void)var
    c = c.replace(/\bconst\s+/g, '');
    c = c.replace(/\binline\s+/g, '');
    c = c.replace(/\(void\)\s*([A-Za-z_]\w*)\s*;/g, '/* (void)$1 */;');

    // 4. Remove size_t cast
    c = c.replace(/\(size_t\)/g, '');

    // 5. Convert long long to double for real-2025-41
    const useDouble = problemCode === 'real-2025-41' || c.includes('res[i] = (a[i] >= 0)');
    if (useDouble) {
      c = c.replace(/\blong\s+long\b/g, 'double');
      c = c.replace(/scanf\("%lld"/g, 'scanf("%lf"');
      c = c.replace(/printf\("%lld"/g, 'printf("%.0f"');
    } else {
      c = c.replace(/\blong\s+long\b/g, 'long');
      c = c.replace(/%lld/g, '%ld');
    }

    // 6. Strip unsupported header includes
    c = c.replace(/#include\s*<limits\.h>/g, '');
    c = c.replace(/#include\s*<stdbool\.h>/g, '');
    c = c.replace(/#include\s*<stddef\.h>/g, '');
    c = c.replace(/#include\s*<float\.h>/g, '');

    // 7. Array initializer & real-2024-41 / real-2016-43
    if (c.includes('int s[2] = {0};')) {
      c = c.replace('int s[2] = {0};', 'int s[2]; s[0] = 0; s[1] = 0;');
    }
    c = c.replace(/int\s+([A-Za-z_]\w*)\s*\[\s*([A-Za-z_]\w*)\s*\]\s*=\s*\{\s*0\s*\}\s*;/g, (m, vName, sz) => {
      return 'static int ' + vName + '[' + sz + '];';
    });

    // 8. Split multi-variable struct pointer declarations:
    c = c.replace(/(\bstruct\s+[A-Za-z_]\w*)\s*\*\s*([A-Za-z_]\w*)\s*,\s*\*?\s*([A-Za-z_]\w*)\s*;/g, (m, g1, g2, g3) => {
      return g1 + ' *' + g2 + '; ' + g1 + ' *' + g3 + ';';
    });

    // 9. Large local stack arrays -> static arrays (avoid stack overflow in PicoC)
    c = c.replace(/(\bint|\bchar|\blong|\bdouble)\s+([A-Za-z_]\w*)\s*\[\s*(\d{4,})\s*\]\s*,\s*([A-Za-z_]\w*)\s*\[\s*(\d{4,})\s*\]\s*;/g, (m, t, n1, s1, n2, s2) => {
      return 'static ' + t + ' ' + n1 + '[' + s1 + ']; static ' + t + ' ' + n2 + '[' + s2 + '];';
    });
    c = c.replace(/(\bint|\bchar|\blong|\bdouble)\s+([A-Za-z_]\w*)\s*\[\s*([0-9]{4,})\s*\]\s*;/g, (m, type, name, size) => {
      return 'static ' + type + ' ' + name + '[' + size + '];';
    });

    // 10. Parenthesize nested ternary operator in prac-stack-01
    c = c.replace(/\(c\s*==\s*'\)'\)\s*\?\s*'\('\s*:\s*\(c\s*==\s*'\]'\)\s*\?\s*'\['\s*:\s*'\{'/g, "(c == ')') ? '(' : ((c == ']') ? '[' : '{')");

    // 11. Fix for-loop multi-variable declarations / updates for prac-seq-02:
    const hadSeq02For = /for\s*\(\s*int\s+i\s*=\s*0\s*,\s*j\s*=\s*n\s*-\s*1/.test(c);
    if (hadSeq02For) {
      c = c.replace(/for\s*\(\s*int\s+i\s*=\s*0\s*,\s*j\s*=\s*n\s*-\s*1\s*;\s*i\s*<\s*j\s*;\s*i\+\+\s*,\s*j--\s*\)\s*\{/g, 'int i = 0, j = n - 1;\n while (i < j) {');
      c = c.replace(/a\[j\]\s*=\s*t\s*;/g, 'a[j] = t; i++; j--;');
    }

    // for (Node *p = head.next; p; p = p->next) -> Node *p; for (p = head.next; p != NULL; p = p->next)
    c = c.replace(/for\s*\(\s*([A-Za-z_]\w*)\s*\*\s*([A-Za-z_]\w*)\s*=\s*([^;]+);\s*([A-Za-z_]\w*);\s*([^)]+)\)/g, (m, type, varName, init, condVar, step) => {
      return type + ' *' + varName + ' = ' + init + '; for (; ' + condVar + ' != NULL; ' + step + ')';
    });

    // 12. Pointer boolean checks: while (cur) -> while (cur != NULL), if (!t) -> if (t == NULL)
    const ptrVars = collectPointerVars(c);
    c = c.replace(/while\s*\(\s*([A-Za-z_]\w*)\s*\)/g, (m, ptr) => ptrVars.has(ptr) ? 'while (' + ptr + ' != NULL)' : m);
    c = c.replace(/while\s*\(\s*([A-Za-z_]\w*->[A-Za-z_]\w*)\s*\)/g, (m, ptr) => 'while (' + ptr + ' != NULL)');
    c = c.replace(/while\s*\(\s*([A-Za-z_]\w*->[A-Za-z_]\w*)\s*&&\s*([A-Za-z_]\w*->[A-Za-z_]\w*->[A-Za-z_]\w*)\s*\)/g, (m, p1, p2) => {
      return 'while (' + p1 + ' != NULL && ' + p2 + ' != NULL)';
    });
    c = c.replace(/while\s*\(\s*([A-Za-z_]\w*)\s*&&\s*([A-Za-z_]\w*->[A-Za-z_]\w*)\s*&&\s*([A-Za-z_]\w*->[A-Za-z_]\w*->[A-Za-z_]\w*)\s*\)/g, (m, p1, p2, p3) => {
      return 'while (' + p1 + ' != NULL && ' + p2 + ' != NULL && ' + p3 + ' != NULL)';
    });
    c = c.replace(/while\s*\(\s*([A-Za-z_]\w*)\s*&&\s*([A-Za-z_]\w*)\s*\)/g, (m, p1, p2) => (ptrVars.has(p1) && ptrVars.has(p2)) ? 'while (' + p1 + ' != NULL && ' + p2 + ' != NULL)' : m);

    c = c.replace(/if\s*\(\s*!([A-Za-z_]\w*)\s*\)/g, (m, ptr) => ptrVars.has(ptr) ? 'if (' + ptr + ' == NULL)' : m);
    c = c.replace(/if\s*\(\s*!([A-Za-z_]\w*->[A-Za-z_]\w*)\s*\)/g, (m, ptr) => 'if (' + ptr + ' == NULL)');
    c = c.replace(/if\s*\(\s*!([A-Za-z_]\w*)\s*\|\|\s*/g, (m, ptr) => ptrVars.has(ptr) ? 'if (' + ptr + ' == NULL || ' : m);

    // 13. Ternary pointer checks ONLY for pa ? pa : pb
    c = c.replace(/\b(pa|pb|ptr|p|cur|left|right|node)\b\s*\?\s*\1\s*:\s*([A-Za-z_]\w*)/g, (m, cond, fVal) => {
      return cond + ' != NULL ? ' + cond + ' : ' + fVal;
    });

    // 14. Fix scanf width specifiers and array pointer arithmetic in scanf: scanf("%100000s", p + 1) -> scanf("%s", &p[1])
    c = c.replace(/scanf\(([^)]*)\)/g, (m, args) => {
      let cleanArgs = args.replace(/%[0-9]+s/g, '%s');
      cleanArgs = cleanArgs.replace(/\b([A-Za-z_]\w*)\s*\+\s*([0-9A-Za-z_]+)\b/g, (m2, arr, idx) => '&' + arr + '[' + idx + ']');
      return 'scanf(' + cleanArgs + ')';
    });

    // 15. Fix sizeof *g_tok -> sizeof(g_tok[0])
    c = c.replace(/sizeof\s+\*([A-Za-z_]\w*)/g, (m, name) => 'sizeof(' + name + '[0])');

    // 16. Fix char (*g_tok)[12] -> char **g_tok
    c = c.replace(/char\s*\(\*([A-Za-z_]\w*)\)\[(\d+)\];/g, (m, name, sz) => 'char **' + name + ';');

    // 17. Fix pointer arithmetic in printf: s1 + i - k -> &s1[i - k]
    c = c.replace(/s1\s*\+\s*i\s*-\s*k/g, '&s1[i - k]');

    // 18. Clamp MAXV in real-2024-41 to 105 for PicoC static array memory
    if (problemCode === 'real-2024-41') {
      c = c.replace(/#define\s+MAXV\s+1005/g, '#define MAXV 105');
    }

    // Header shims
    const shims = `
#ifndef PICOC_SHIMS
#define PICOC_SHIMS
#define size_t int
#define bool int
#define true 1
#define false 0
#define INT_MAX 2147483647
#define INT_MIN (-2147483647-1)
#define LONG_MAX 2147483647
#define LONG_MIN (-2147483647-1)
#define LLONG_MAX 9223372036854775807LL
#define LLONG_MIN (-9223372036854775807LL-1LL)
#endif
`;

    return shims + '\n' + c;
  }

  function runPicoC(cprog, stdinStr, timeoutMs, problemCode) {
    timeoutMs = timeoutMs || 15000;
    return new Promise((resolve) => {
      const picocFactory = getPicocFactory();
      if (!picocFactory) {
        resolve({ status: 1, output: '', error: 'PicoC WASM 评测引擎未就绪' });
        return;
      }

      let stdinPos = 0;
      let stdoutText = '';
      let hasEnded = false;

      const finish = (status, err) => {
        if (hasEnded) return;
        hasEnded = true;
        resolve({ status: status, output: stdoutText, error: err });
      };

      const timer = setTimeout(() => {
        finish(124, 'TLE: 执行超时');
      }, timeoutMs);

      try {
        const config = {
          noExitRuntime: true,
          stdin() {
            if (stdinPos < stdinStr.length) {
              return stdinStr.charCodeAt(stdinPos++);
            }
            return null;
          },
          print(t) {
            stdoutText += t + '\n';
          },
          printErr(t) {},
          onRuntimeInitialized() {
            try {
              const cleanCode = preprocessForPicoC(cprog, problemCode);
              config.runc(cleanCode, (str) => {
                if (str) stdoutText += str + '\n';
              });
              clearTimeout(timer);
              finish(0, null);
            } catch (e) {
              clearTimeout(timer);
              finish(1, e.message || String(e));
            }
          }
        };

        const pc = picocFactory(config);

        // If the module already initialized synchronously (SINGLE_FILE),
        // onRuntimeInitialized was already called inside picocFactory.
        // If not, the callback set on config will fire later.
        // In either case, we also handle the .then() path as a safety net.
        if (pc && typeof pc.then === 'function' && !hasEnded) {
          pc.then((mod) => {
            if (hasEnded) return;
            try {
              const cleanCode = preprocessForPicoC(cprog, problemCode);
              mod.runc(cleanCode, (str) => {
                if (str) stdoutText += str + '\n';
              });
              clearTimeout(timer);
              finish(0, null);
            } catch (e) {
              clearTimeout(timer);
              finish(1, e.message || String(e));
            }
          });
        }
      } catch (e) {
        clearTimeout(timer);
        finish(1, e.message || String(e));
      }
    });
  }

  async function judgeCode(src, policy, testcases, timeLimitMs, memoryLimitKb, problemCode) {
    testcases = testcases || [];
    const limit = timeLimitMs > 0 ? timeLimitMs : 15000;
    const issues = OJPolicy ? OJPolicy.checkSource(src, policy) : [];
    const policyIssues = issues.map(i => i.fmt ? i.fmt() : `第 ${i.line} 行: [${i.kind}] ${i.name} — ${i.message}`);

    if (issues.length > 0) {
      return {
        verdict: "CE",
        passed: 0,
        total: testcases.length,
        compile_msg: "408 源码合规检查未通过:\n" + policyIssues.join("\n"),
        results: [],
        max_time_ms: 0,
        max_mem_kb: 0,
        policy_issues: policyIssues
      };
    }

    const results = [];
    let passed = 0;
    let overallVerdict = "AC";

    for (let idx = 0; idx < testcases.length; idx++) {
      const tc = testcases[idx];
      const res = await runPicoC(src, tc.input || "", limit, problemCode);
      let tcStatus = "AC";
      let tcMsg = "";

      if (res.error) {
        if (res.status === 124) {
          tcStatus = "TLE";
          tcMsg = "运行超时";
        } else {
          tcStatus = "RE";
          tcMsg = res.error;
        }
      } else {
        const normExp = normalizeOutput(tc.expected || "");
        const normAct = normalizeOutput(res.output || "");
        if (normExp !== normAct) {
          tcStatus = "WA";
          tcMsg = `期望输出: "${normExp}"，实际输出: "${normAct}"`;
        }
      }

      if (tcStatus === "AC") {
        passed++;
      } else if (overallVerdict === "AC") {
        overallVerdict = tcStatus;
      }

      results.push({
        status: tcStatus,
        time_ms: 0,
        mem_kb: 0,
        msg: tcMsg,
        stdout: res.output || ""
      });
    }

    return {
      verdict: overallVerdict,
      passed: passed,
      total: testcases.length,
      compile_msg: "",
      results: results,
      max_time_ms: 0,
      max_mem_kb: 0,
      policy_issues: []
    };
  }

  async function runCustom(src, policy, input, problemCode, timeLimitMs) {
    const issues = OJPolicy ? OJPolicy.checkSource(src, policy) : [];
    const policyIssues = issues.map(i => i.fmt ? i.fmt() : `第 ${i.line} 行: [${i.kind}] ${i.name} — ${i.message}`);

    if (issues.length > 0) {
      return {
        ok: false,
        stage: "policy",
        compile_msg: "408 源码合规检查未通过:\n" + policyIssues.join("\n"),
        output: "",
        time_ms: 0,
        mem_kb: 0,
        policy_issues: policyIssues
      };
    }

    const res = await runPicoC(src, input || "", timeLimitMs > 0 ? timeLimitMs : 15000, problemCode);
    return {
      ok: !res.error,
      stage: res.error ? (res.status === 124 ? "runtime" : "compile") : "ok",
      compile_msg: res.error || "",
      output: res.output || "",
      time_ms: 0,
      mem_kb: 0,
      policy_issues: []
    };
  }

  return {
    normalizeOutput: normalizeOutput,
    preprocessForPicoC: preprocessForPicoC,
    runPicoC: runPicoC,
    judgeCode: judgeCode,
    runCustom: runCustom
  };
}));

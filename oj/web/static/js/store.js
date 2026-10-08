/* 408OJ 本地存储模块 (localStorage 持久化)。
 * 管理离线环境下的提交记录、刷题 AC 状态、草稿代码。
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.OJStore = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const SUBMISSIONS_KEY = '408oj_submissions';
  const SOLVED_KEY = '408oj_solved';
  const DRAFT_PREFIX = 'oj-code-';
  const LEGACY_DRAFT_PREFIX = '408oj_draft_';
  const MAX_SUBMISSIONS = 100;

  function safeJSONParse(str, fallback) {
    try {
      return JSON.parse(str) || fallback;
    } catch (e) {
      return fallback;
    }
  }

  function safeJSONStringify(val) {
    try {
      return JSON.stringify(val);
    } catch (e) {
      return '[]';
    }
  }

  function cleanOldDrafts(preserveKey) {
    if (typeof localStorage === 'undefined') return;
    try {
      const keysToRemove = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && (k.startsWith(DRAFT_PREFIX) || k.startsWith(LEGACY_DRAFT_PREFIX))) {
          if (preserveKey && k === preserveKey) continue;
          keysToRemove.push(k);
        }
      }
      keysToRemove.forEach(k => {
        try { localStorage.removeItem(k); } catch (e) {}
      });
    } catch (e) {}
  }

  function safeSetSubmissions(subs) {
    if (typeof localStorage === 'undefined') return false;
    try {
      localStorage.setItem(SUBMISSIONS_KEY, safeJSONStringify(subs));
      return true;
    } catch (e) {
      return false;
    }
  }

  function getSubmissions(problemCode) {
    if (typeof localStorage === 'undefined') return [];
    let str = null;
    try {
      str = localStorage.getItem(SUBMISSIONS_KEY);
    } catch (e) {}
    const subs = safeJSONParse(str, []);
    if (problemCode) {
      return subs.filter(s => s.problemCode === problemCode || s.problem_code === problemCode);
    }
    return subs;
  }

  function getSubmissionById(sid) {
    const subs = getSubmissions();
    return subs.find(s => String(s.id) === String(sid)) || null;
  }

  function saveSubmission(sub) {
    if (typeof localStorage === 'undefined') return sub;
    let subs = getSubmissions();
    const maxId = subs.reduce((max, s) => {
      const nid = Number(s.id) || 0;
      return nid > max ? nid : max;
    }, 0);
    const nextId = maxId + 1;

    const newSub = Object.assign({
      id: nextId,
      created_at: Math.floor(Date.now() / 1000)
    }, sub);

    // 标准化字段命名，确保前端与 Python 后端视图一致
    newSub.problem_code = newSub.problem_code || newSub.problemCode;
    newSub.problem_title = newSub.problem_title || newSub.problemTitle || newSub.problem_code;
    newSub.max_time_ms = newSub.max_time_ms !== undefined ? newSub.max_time_ms : (newSub.maxTimeMs || 0);
    newSub.max_mem_kb = newSub.max_mem_kb !== undefined ? newSub.max_mem_kb : (newSub.maxMemKb || 0);
    newSub.compile_msg = newSub.compile_msg !== undefined ? newSub.compile_msg : (newSub.compileMsg || '');
    newSub.policy_issues = newSub.policy_issues || newSub.policyIssues || [];

    subs.unshift(newSub);

    // 限制最大保留数量，防止无休止膨胀
    if (subs.length > MAX_SUBMISSIONS) {
      subs = subs.slice(0, MAX_SUBMISSIONS);
    }

    // 尝试写入 localStorage
    let saved = safeSetSubmissions(subs);
    if (!saved) {
      // 空间超限：清理非当前题目的旧草稿重试
      const curDraftKey = DRAFT_PREFIX + (newSub.problem_code || '');
      cleanOldDrafts(curDraftKey);
      saved = safeSetSubmissions(subs);
    }

    if (!saved) {
      // 仍然超限：逐步裁剪旧提交记录 (100 -> 50 -> 20 -> 10 -> 5)
      const ratios = [0.5, 0.2, 0.1, 0.05];
      for (const ratio of ratios) {
        const keepCount = Math.max(1, Math.floor(MAX_SUBMISSIONS * ratio));
        if (subs.length > keepCount) {
          subs = subs.slice(0, keepCount);
          if (safeSetSubmissions(subs)) {
            saved = true;
            break;
          }
        }
      }
    }

    // 更新 AC / Status 映射
    const pcode = newSub.problem_code;
    if (pcode) {
      const solvedMap = getSolvedMap();
      const curStatus = solvedMap[pcode];
      if (newSub.verdict === 'AC') {
        solvedMap[pcode] = 'AC';
      } else if (!curStatus) {
        solvedMap[pcode] = newSub.verdict;
      }
      try {
        localStorage.setItem(SOLVED_KEY, safeJSONStringify(solvedMap));
      } catch (e) {
        // 忽略 SOLVED_KEY 写入错误
      }
    }

    return newSub;
  }

  function getSolvedMap() {
    if (typeof localStorage === 'undefined') return {};
    let str = null;
    try {
      str = localStorage.getItem(SOLVED_KEY);
    } catch (e) {}
    return safeJSONParse(str, {});
  }

  function saveDraft(code, sourceCode) {
    if (!code || typeof localStorage === 'undefined') return;
    const key = DRAFT_PREFIX + code;
    try {
      localStorage.setItem(key, sourceCode || '');
    } catch (e) {
      // 配额超限：清理其他题目的旧草稿重试
      cleanOldDrafts(key);
      try {
        localStorage.setItem(key, sourceCode || '');
      } catch (_) {}
    }
  }

  function getDraft(code) {
    if (!code || typeof localStorage === 'undefined') return '';
    try {
      const val = localStorage.getItem(DRAFT_PREFIX + code);
      if (val !== null) return val;
      return localStorage.getItem(LEGACY_DRAFT_PREFIX + code) || '';
    } catch (e) {
      return '';
    }
  }

  function getStats() {
    const subs = getSubmissions();
    const solvedMap = getSolvedMap();
    const acCount = subs.filter(s => s.verdict === 'AC').length;
    const solvedProblemCount = Object.keys(solvedMap).filter(k => solvedMap[k] === 'AC').length;
    return {
      submissions: subs.length,
      ac: acCount,
      solved: solvedProblemCount
    };
  }

  return {
    getSubmissions: getSubmissions,
    getSubmissionById: getSubmissionById,
    saveSubmission: saveSubmission,
    getSolvedMap: getSolvedMap,
    saveDraft: saveDraft,
    getDraft: getDraft,
    getStats: getStats,
    cleanOldDrafts: cleanOldDrafts
  };
}));

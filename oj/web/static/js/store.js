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
  const DRAFT_PREFIX = '408oj_draft_';

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

  function getSubmissions(problemCode) {
    if (typeof localStorage === 'undefined') return [];
    const subs = safeJSONParse(localStorage.getItem(SUBMISSIONS_KEY), []);
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
    const subs = getSubmissions();
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
    localStorage.setItem(SUBMISSIONS_KEY, safeJSONStringify(subs));

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
      localStorage.setItem(SOLVED_KEY, safeJSONStringify(solvedMap));
    }

    return newSub;
  }

  function getSolvedMap() {
    if (typeof localStorage === 'undefined') return {};
    return safeJSONParse(localStorage.getItem(SOLVED_KEY), {});
  }

  function saveDraft(code, sourceCode) {
    if (!code || typeof localStorage === 'undefined') return;
    localStorage.setItem(DRAFT_PREFIX + code, sourceCode || '');
  }

  function getDraft(code) {
    if (!code || typeof localStorage === 'undefined') return '';
    return localStorage.getItem(DRAFT_PREFIX + code) || '';
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
    getStats: getStats
  };
}));

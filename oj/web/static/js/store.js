/* 408OJ 本地存储模块 (localStorage / IndexedDB持久化)。
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
      return subs.filter(s => s.problemCode === problemCode);
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
    const id = Date.now();
    const newSub = Object.assign({
      id: id,
      created_at: Math.floor(Date.now() / 1000)
    }, sub);

    subs.unshift(newSub);
    localStorage.setItem(SUBMISSIONS_KEY, safeJSONStringify(subs));

    // 更新 AC / Status 映射
    const solvedMap = getSolvedMap();
    const curStatus = solvedMap[sub.problemCode];
    if (sub.verdict === 'AC') {
      solvedMap[sub.problemCode] = 'AC';
    } else if (!curStatus) {
      solvedMap[sub.problemCode] = sub.verdict;
    }
    localStorage.setItem(SOLVED_KEY, safeJSONStringify(solvedMap));

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

const assert = require('assert');

// 构造 Mock localStorage 环境支持存储配额模拟与 QuotaExceededError 抛错
function createMockLocalStorage(maxBytes = 100000) {
  let store = {};
  return {
    maxBytes,
    get length() {
      return Object.keys(store).length;
    },
    key(i) {
      return Object.keys(store)[i] || null;
    },
    getItem(key) {
      return store.hasOwnProperty(key) ? store[key] : null;
    },
    setItem(key, value) {
      const valStr = String(value);
      const newStore = Object.assign({}, store, { [key]: valStr });
      const totalBytes = Object.keys(newStore).reduce((acc, k) => acc + k.length + newStore[k].length, 0);
      if (totalBytes > this.maxBytes) {
        const err = new Error('Setting the value of \'' + key + '\' exceeded the quota.');
        err.name = 'QuotaExceededError';
        throw err;
      }
      store[key] = valStr;
    },
    removeItem(key) {
      delete store[key];
    },
    clear() {
      store = {};
    },
    _getStore() { return store; }
  };
}

global.localStorage = createMockLocalStorage(1000000);
const OJStore = require('../oj/web/static/js/store.js');

// Test 1: 正常提交保存与上限剪裁 (MAX_SUBMISSIONS = 100)
{
  global.localStorage.clear();
  for (let i = 1; i <= 120; i++) {
    OJStore.saveSubmission({
      problem_code: 'p-' + (i % 5),
      verdict: i % 2 === 0 ? 'AC' : 'WA',
      code: 'int main(){ return ' + i + '; }'
    });
  }
  const subs = OJStore.getSubmissions();
  assert.strictEqual(subs.length, 100, '应限制最多保留 100 条提交');
  assert.strictEqual(subs[0].id, 120, '最新提交应在数组首位');
  console.log('Test 1 Passed: 正常提交保存与上限 100 剪裁');
}

// Test 2: 当超配额 (QuotaExceededError) 时，自动清理旧草稿与剪裁提交记录
{
  global.localStorage.clear();
  // 设置较小的 Mock 配额 (例如 5KB)
  global.localStorage.maxBytes = 5000;

  // 写入若干旧草稿
  global.localStorage.setItem('oj-code-p1', 'x'.repeat(1000));
  global.localStorage.setItem('oj-code-p2', 'y'.repeat(1000));
  global.localStorage.setItem('oj-code-p3', 'z'.repeat(1000));

  // 尝试连续保存大体积提交记录
  let errorCount = 0;
  for (let i = 1; i <= 20; i++) {
    try {
      OJStore.saveSubmission({
        problem_code: 'real-2012-41',
        verdict: 'AC',
        code: 'int main(){ /* ' + 'A'.repeat(300) + ' */ return 0; }',
        compile_msg: 'compilation detail ' + i
      });
    } catch (e) {
      errorCount++;
    }
  }

  assert.strictEqual(errorCount, 0, 'saveSubmission 在配额满时不应抛出未捕获异常');
  const subs = OJStore.getSubmissions();
  assert.ok(subs.length > 0 && subs.length <= 20, '应当保留部分可用提交记录');
  console.log('Test 2 Passed: 存储超配额时自动清理草稿与自动裁剪提交');
}

// Test 3: 草稿保存 saveDraft / getDraft 兼容性与配额超限保护
{
  global.localStorage.clear();
  global.localStorage.maxBytes = 2000;

  OJStore.saveDraft('real-2012-41', '#include <stdio.h>\nint main(){ return 0; }');
  assert.strictEqual(OJStore.getDraft('real-2012-41'), '#include <stdio.h>\nint main(){ return 0; }');

  // 兼容旧前缀 408oj_draft_
  global.localStorage.setItem('408oj_draft_old-01', 'legacy draft code');
  assert.strictEqual(OJStore.getDraft('old-01'), 'legacy draft code');

  // 当超出配额时 saveDraft 不抛错，并尝试清理旧草稿
  assert.doesNotThrow(() => {
    OJStore.saveDraft('new-big', 'K'.repeat(3000));
  });
  console.log('Test 3 Passed: 草稿读写、前缀兼容与配额保护');
}

console.log('ALL store.js tests passed!');

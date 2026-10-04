// 由 pytest 经 node 执行：编辑器回车缩进 computeEnter 与高亮 highlight 的行为测试。
const assert = require('assert');
const { computeEnter, highlight } = require('../oj/web/static/js/editor.js');

function enter(src, pos) {
  const before = src.slice(0, pos);
  const after = src.slice(pos);
  const { insert, caret } = computeEnter(before, after, pos);
  const result = before + insert + after;
  return { result, caret };
}

// 1) 继承上一行缩进
{
  const src = 'int main(void){\n    int x = 1;\n}';
  const pos = src.indexOf('1;') + 2; // 行尾
  const { result, caret } = enter(src, pos);
  const nextLine = result.split('\n')[2];
  assert.strictEqual(nextLine, '    ');
  assert.strictEqual(caret, pos + 5); // \n + 4 spaces
}

// 2) 以 { 结尾的行，下一行更深一级
{
  const src = 'if (x) {';
  const { result } = enter(src, src.length);
  assert.ok(result.endsWith('if (x) {\n    '));
}

// 3) 嵌套缩进 + {：二级缩进
{
  const src = '    while (p) {';
  const { result } = enter(src, src.length);
  assert.ok(result.endsWith('\n        '), result);
}

// 4) 空块：生成 { \n | \n }，光标居中
{
  const src = 'if (x) {}';
  const pos = src.indexOf('{}') + 1; // 在 { 与 } 之间
  const { result, caret } = enter(src, pos);
  assert.strictEqual(result, 'if (x) {\n    \n}');
  assert.strictEqual(caret, pos + 5);
}

// 5) 光标位于行中间：只影响插入点
{
  const src = '    int ab = 0;';
  const pos = src.indexOf('ab');
  const { result } = enter(src, pos);
  assert.strictEqual(result, '    int \n    ab = 0;');
}

// 6) 高亮：把关键字/类型/字符串/注释包上 token span
{
  const html = highlight('#include <stdio.h>\nint main(){ // hi\n  int x = "a"; return 0;\n}\n');
  assert.ok(html.includes('tok-p'), '预处理标记');
  assert.ok(html.includes('tok-k'), '关键字');
  assert.ok(html.includes('tok-t'), '类型');
  assert.ok(html.includes('tok-c'), '注释');
  assert.ok(html.includes('tok-s'), '字符串');
  assert.ok(!html.includes('<stdio.h>') && html.includes('&lt;stdio.h&gt;'), '尖括号转义');
}

console.log('editor.js tests OK');

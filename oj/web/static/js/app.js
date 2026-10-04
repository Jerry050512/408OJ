/* 408OJ 全局脚本：主题切换 + 小工具 */

(function () {
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    const sun = document.getElementById('iconSun');
    const moon = document.getElementById('iconMoon');
    if (sun && moon) {
      sun.style.display = t === 'dark' ? '' : 'none';
      moon.style.display = t === 'dark' ? 'none' : '';
    }
  }
  window.applyTheme = applyTheme;
  document.addEventListener('DOMContentLoaded', function () {
    applyTheme(localStorage.getItem('oj-theme') || 'dark');
    const btn = document.getElementById('themeBtn');
    if (btn) btn.addEventListener('click', function () {
      const cur = localStorage.getItem('oj-theme') || 'dark';
      const nxt = cur === 'dark' ? 'light' : 'dark';
      localStorage.setItem('oj-theme', nxt);
      applyTheme(nxt);
    });
  });
})();

function copyText(btn, text) {
  navigator.clipboard.writeText(text).then(function () {
    const old = btn.textContent;
    btn.textContent = '已复制 ✓';
    setTimeout(function () { btn.textContent = old; }, 1200);
  });
}

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
    let savedTheme = 'dark';
    try { savedTheme = localStorage.getItem('oj-theme') || 'dark'; } catch (e) {}
    applyTheme(savedTheme);

    const btn = document.getElementById('themeBtn');
    if (btn) btn.addEventListener('click', function () {
      let cur = 'dark';
      try { cur = localStorage.getItem('oj-theme') || 'dark'; } catch (e) {}
      const nxt = cur === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('oj-theme', nxt); } catch (e) {}
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

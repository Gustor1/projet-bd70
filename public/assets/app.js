'use strict';
document.querySelectorAll('[data-print]').forEach(b => b.addEventListener('click', () => window.print()));
document.querySelectorAll('[data-confirm]').forEach(b => b.addEventListener('click', e => { if (!window.confirm(b.dataset.confirm)) e.preventDefault(); }));
let edited = false;
document.addEventListener('input', () => { edited = true; });
if (document.querySelector('[data-refresh]')) window.setTimeout(() => { if (!edited && !document.hidden) window.location.reload(); }, 30000);

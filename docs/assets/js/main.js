const track = document.getElementById('tickerTrack');
  for (let i = 0; i < 2; i++) {
    for (let j = 0; j < 18; j++) {
      const geneId = Math.floor(Math.random() * 20531);
      const val = (Math.random() * 15).toFixed(2);
      const el = document.createElement('div');
      el.className = 'ticker-item';
      el.innerHTML = `<span class="gid">gene_${geneId}</span><span class="gval">${val}</span>`;
      track.appendChild(el);
    }
  }

/* ---------- Menú móvil ---------- */
(function () {
  const toggle = document.getElementById('navToggle');
  const wrap = document.querySelector('.nav-wrap');
  const links = document.getElementById('tabsBar');
  if (!toggle || !wrap) return;

  const close = () => {
    wrap.classList.remove('menu-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Abrir menú');
  };

  toggle.addEventListener('click', () => {
    const open = wrap.classList.toggle('menu-open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
  });

  if (links) links.addEventListener('click', (e) => {
    if (e.target.closest('a')) setTimeout(close, 0);
  });

  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
})();

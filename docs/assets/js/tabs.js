(function () {
  const triggers = document.querySelectorAll('[data-tab]');
  const panels = document.querySelectorAll('.tab-panel');

  function activar(tab) {
    panels.forEach(p => {
      const visible = p.getAttribute('data-tab') === tab;
      p.hidden = !visible;
      if (visible) p.setAttribute('data-state', 'active');
      else p.removeAttribute('data-state');
    });

    document.querySelectorAll('.tab-btn').forEach(b => {
      b.setAttribute('aria-selected', b.getAttribute('data-tab') === tab ? 'true' : 'false');
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  triggers.forEach(t => {
    t.addEventListener('click', () => activar(t.getAttribute('data-tab')));
  });
})();
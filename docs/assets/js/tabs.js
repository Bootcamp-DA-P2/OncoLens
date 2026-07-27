(function () {
  const links  = document.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('.tab-panel');
  if (!links.length || !panels.length) return;

  // Marca la pestaña activa según el panel visible
  const io = new IntersectionObserver(entradas => {
    entradas.forEach(e => {
      if (!e.isIntersecting) return;
      const id = e.target.id;
      links.forEach(l => {
        const suyo = l.getAttribute('href') === '#' + id;
        l.setAttribute('aria-selected', suyo ? 'true' : 'false');
      });
      e.target.setAttribute('data-state', 'active');
    });
  }, { rootMargin: '-45% 0px -45% 0px' });

  panels.forEach(p => io.observe(p));

  // Desplazamiento suave al pulsar
  links.forEach(l => {
    l.addEventListener('click', ev => {
      const destino = document.querySelector(l.getAttribute('href'));
      if (!destino) return;
      ev.preventDefault();
      destino.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
})();
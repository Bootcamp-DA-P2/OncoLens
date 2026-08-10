/* ============================================
   ONCOSLENS TOUR - NAVEGACIÓN
   ============================================ */

// Mapeo de apartados
const TOUR_APARTADOS = [
    { id: 1, titulo: 'Introducción',             nombre: '01-intro-oncolens',      url: '../01-intro-oncolens/index-01intro.html' },
    { id: 2, titulo: 'Datos y Metodología',      nombre: '02-datos-metodologia',   url: '../02-datos-metodologia/index-02datos.html' },
    { id: 3, titulo: 'Resultados Clave',         nombre: '03-resultados',          url: '../03-resultados/index-03resultados.html' },
    { id: 4, titulo: 'Demo',                     nombre: '04-demo',                url: '../04-demo/index-04demo.html' },
    { id: 5, titulo: 'Limitaciones',             nombre: '05-limitaciones',        url: '../05-limitaciones/index-05limitaciones.html' },
    { id: 6, titulo: 'Desarrollos Futuros',      nombre: '06-desarrollos-futuros', url: '../06-desarrollos-futuros/index-06desarrollos.html' },
    { id: 7, titulo: 'Equipo y Agradecimientos', nombre: '07-equipo-agradecimientos', url: '../07-equipo-agradecimientos/index-07equipo.html' }
];

// Detectar apartado actual
function detectarApartadoActual() {
    const pathname = window.location.pathname;
    return TOUR_APARTADOS.find(apt => pathname.includes(apt.nombre));
}

// Actualizar indicador de progreso
function actualizarProgreso() {
    const apartado = detectarApartadoActual();
    const progressEl = document.querySelector('.tour-progress');
    
    if (progressEl && apartado) {
            progressEl.innerHTML =
                `<span class="prog-num">${String(apartado.id).padStart(2, '0')}</span>` +
                `<span class="prog-tit"> · ${apartado.titulo}</span>`;    }
}

// Navegar al siguiente apartado
function nextApartado() {
    const apartado = detectarApartadoActual();
    
    if (!apartado) {
        console.warn('No se pudo detectar el apartado actual');
        return;
    }
    
    const siguiente = TOUR_APARTADOS[apartado.id];
    
    if (siguiente) {
        window.location.href = siguiente.url;
    } else {
        // Si es el último apartado, ir al inicio
        console.log('Fin del tour');
        window.location.href = '/';
    }
}

// Navegación por teclado
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') {
        e.preventDefault();
        nextApartado();
    }
    
    if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevApartado();
    }
});

// Navegar al apartado anterior
function prevApartado() {
    const apartado = detectarApartadoActual();
    
    if (!apartado) return;
    
    const anterior = TOUR_APARTADOS[apartado.id - 2]; // -2 porque índice empieza en 0
    
    if (anterior) {
        window.location.href = anterior.url;
    }
}

// Gestión de scroll snap
function handleScrollSnap() {
    const container = document.querySelector('.tour-container');
    
    if (!container) return;
    
    // Detectar si el usuario llegó al final
    container.addEventListener('scroll', () => {
        const scrollHeight = container.scrollHeight;
        const scrollTop = container.scrollTop;
        const clientHeight = container.clientHeight;
        
        // Si está cerca del final, mostrar opción de ir al siguiente
        if (scrollTop + clientHeight >= scrollHeight - 100) {
            // Automáticamente mostrar/destacar botón next
            const btnNext = document.querySelector('.tour-btn-next');
            if (btnNext) {
                btnNext.style.opacity = '1';
            }
        }
    });
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    actualizarProgreso();
    handleScrollSnap();
    
    // Agregar event listener al botón siguiente
    const btnNext = document.querySelector('.tour-btn-next');
    if (btnNext) {
        btnNext.addEventListener('click', nextApartado);
    }
    
    // Swipe gestures para móvil (opcional)
    setupSwipeGestures();
});

// Gestos táctiles para móvil
function setupSwipeGestures() {
    let x0 = 0, y0 = 0, t0 = 0;

    document.addEventListener('touchstart', (e) => {
        x0 = e.changedTouches[0].screenX;
        y0 = e.changedTouches[0].screenY;
        t0 = Date.now();
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
        const dx = e.changedTouches[0].screenX - x0;
        const dy = e.changedTouches[0].screenY - y0;
        const dt = Date.now() - t0;

        // Debe ser horizontal, amplio y rápido; si no, es un scroll.
        if (Math.abs(dx) < 90) return;              // recorrido mínimo
        if (Math.abs(dx) < Math.abs(dy) * 2.5) return; // claramente horizontal
        if (dt > 600) return;                        // gesto deliberado, no arrastre lento

        if (dx < 0) nextApartado();
        else prevApartado();
    }, { passive: true });
}

// Funciones útiles para navegación avanzada
function irApartado(numero) {
    if (numero < 1 || numero > TOUR_APARTADOS.length) {
        console.warn('Número de apartado inválido');
        return;
    }
    window.location.href = TOUR_APARTADOS[numero - 1].url;
}

function mostrarMenuApartados() {
    const menu = TOUR_APARTADOS.map((apt, idx) => 
        `<a href="${apt.url}" class="tour-menu-item">${apt.id}. ${apt.titulo}</a>`
    ).join('');
    
    console.log('Apartados disponibles:', menu);
}

// Analítica simple (opcional)
function registrarVisita() {
    const apartado = detectarApartadoActual();
    if (apartado && window.gtag) {
        gtag('event', 'tour_apartado', {
            apartado_id: apartado.id,
            apartado_nombre: apartado.titulo
        });
    }
}

// Ejecutar al cargar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', registrarVisita);
} else {
    registrarVisita();
}

// Animación del gráfico de barras (capítulo 02)
(function () {
  const chart = document.getElementById('chart');
  if (!chart) return;
  new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (e.isIntersecting) { chart.classList.add('is-live'); obs.disconnect(); }
    });
  }, { threshold: 0.35 }).observe(chart);
})();

// Texto mecanografiado (cualquier elemento con .typed y data-texto)
document.querySelectorAll('.typed').forEach(function (el) {
  const salida = el.querySelector('.typed-txt');
  const bruto  = el.dataset.texto || '';
  if (!salida || !bruto) return;

  const quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let lanzado = false;

  const trozos = [];
  bruto.split(/(\*[^*]+\*|_[^_]+_)/g).forEach(p => {
    if (!p) return;
    if (p.startsWith('*') && p.endsWith('*'))      trozos.push({ t: p.slice(1, -1), c: 'typed-hl' });
    else if (p.startsWith('_') && p.endsWith('_')) trozos.push({ t: p.slice(1, -1), c: 'typed-ac' });
    else                                           trozos.push({ t: p, c: null });
  });

  const total = trozos.reduce((n, s) => n + s.t.length, 0);
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

  function pintar(n) {
    let out = '', usados = 0;
    for (const s of trozos) {
      if (usados >= n) break;
      const parte = s.t.slice(0, n - usados);
      usados += parte.length;
      if (!parte) continue;
      out += s.c ? '<b class="' + s.c + '">' + esc(parte) + '</b>' : esc(parte);
    }
    salida.innerHTML = out;
  }

  function escribir() {
    if (lanzado) return;
    lanzado = true;
    if (quieto) { pintar(total); el.classList.add('is-done'); return; }
    let i = 0;
    (function paso() {
      pintar(++i);
      if (i < total) setTimeout(paso, 42);
      else el.classList.add('is-done');
    })();
  }

  function visible() {
    const r = el.getBoundingClientRect();
    return r.top < window.innerHeight * 0.85 && r.bottom > 0;
  }

  const cont = document.querySelector('.tour-container');
  if (cont) cont.addEventListener('scroll', () => { if (visible()) escribir(); }, { passive: true });
  window.addEventListener('resize', () => { if (visible()) escribir(); });
  if (visible()) escribir();
});

/*// Botón flotante de siguiente apartado
(function () {
  const fab = document.getElementById('fab');
  const cont = document.querySelector('.tour-container');
  if (!fab || !cont) return;

  function check() {
    const cerca = cont.scrollTop + cont.clientHeight >= cont.scrollHeight - 260;
    fab.classList.toggle('is-on', cerca);
  }

  cont.addEventListener('scroll', check, { passive: true });
  check();
})();*/

// Barra inferior: progreso y aviso de final
(function () {
  const prog = document.getElementById('barProg');
  const cont = document.querySelector('.tour-container');
  const next = document.querySelector('.tour-bar-next');
  if (!cont) return;

  function check() {
    const max = cont.scrollHeight - cont.clientHeight;
    const pct = max > 0 ? cont.scrollTop / max : 0;
    if (prog) prog.style.width = (pct * 100) + '%';
    if (next) next.classList.toggle('is-vis', pct > 0.9);
    if (next) next.classList.toggle('is-end', pct > 0.97);
  }

  cont.addEventListener('scroll', check, { passive: true });
  window.addEventListener('resize', check);
  check();
})();


(function () {
  const el = document.getElementById('nbs');
  if (!el) return;
  new IntersectionObserver((es, obs) => {
    es.forEach(e => {
      if (e.isIntersecting) { el.classList.add('is-live'); obs.disconnect(); }
    });
  }, { threshold: 0.3 }).observe(el);
})();


(function () {
  const el = document.getElementById('comp');
  if (!el) return;
  new IntersectionObserver((es, obs) => {
    es.forEach(e => {
      if (e.isIntersecting) { el.classList.add('is-live'); obs.disconnect(); }
    });
  }, { threshold: 0.3 }).observe(el);
})();
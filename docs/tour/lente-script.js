/* Añadir al final de script-tour.js */

(function(){
  const lens=document.getElementById('lens');
  const A=document.getElementById('lensA'), B=document.getElementById('lensB');
  const fovN=document.getElementById('fovN'), fovU=document.getElementById('fovU');
  const barN=document.getElementById('barN'), barU=document.getElementById('barU');
  const magN=document.getElementById('magN');
  const play=document.getElementById('lensPlay');
  if(!lens) return;

  const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;

  // Punto de fuga: nudillos, la zona con mayor detalle real de la foto
  A.style.transformOrigin='60% 52%';
  B.style.transformOrigin='70% 45%';

  const FADE_IN=0.34, FADE_OUT=0.54;   // ventana de solape entre capas
  const FOV0=280, FOV1=1.2;            // campo de visión en mm
  const DUR=4600;                      // duración del descenso

  const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
  const map=(v,a,b)=>clamp((v-a)/(b-a),0,1);
  const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;

  function fmt(mm){
    if(mm>=100) return [(mm/10).toFixed(1).replace('.',','),'cm'];
    if(mm>=1)   return [mm.toFixed(1).replace('.',','),'mm'];
    return [Math.round(mm*1000).toString(),'µm'];
  }

  let p=0;
  function render(){
    const sA=Math.pow(3.4,map(p,0,0.55));
    const oA=1-map(p,FADE_IN,FADE_OUT);
    A.style.transform='scale('+sA.toFixed(4)+')';
    A.style.opacity=oA.toFixed(3);
    A.style.filter=(!reduce&&oA>0&&oA<1)?'blur('+((1-oA)*4).toFixed(2)+'px)':'none';

    const sB=0.88*Math.pow(3.2,map(p,FADE_IN,1));
    const oB=map(p,FADE_IN,FADE_OUT);
    B.style.transform='scale('+sB.toFixed(4)+')';
    B.style.opacity=oB.toFixed(3);
    B.style.filter=(!reduce&&oB>0&&oB<1)?'blur('+((1-oB)*3).toFixed(2)+'px)':'none';

    const fov=FOV0*Math.pow(FOV1/FOV0,p);
    const [n,u]=fmt(fov);
    fovN.textContent=n; fovU.textContent=u;
    barN.textContent=n; barU.textContent=u;
    magN.textContent=Math.round(FOV0/fov);
  }

  // ── reproducción automática ──
  let raf=null, t0=null;
  function step(ts){
    if(t0===null) t0=ts;
    const k=clamp((ts-t0)/DUR,0,1);
    p=ease(k);
    render();
    if(k<1){ raf=requestAnimationFrame(step); }
    else{ lens.classList.remove('is-running'); raf=null; }
  }
  function run(){
    if(raf) cancelAnimationFrame(raf);
    t0=null; p=0; lens.classList.add('is-running');
    if(reduce){ p=1; render(); lens.classList.remove('is-running'); return; }
    raf=requestAnimationFrame(step);
  }
  play.addEventListener('click',run);

  // ── arrastre para explorar ──
  let dragging=false, y0=0, p0=0;
  lens.addEventListener('pointerdown',e=>{
    if(raf){ cancelAnimationFrame(raf); raf=null; lens.classList.remove('is-running'); }
    dragging=true; y0=e.clientY; p0=p;
    lens.setPointerCapture(e.pointerId);
  });
  lens.addEventListener('pointermove',e=>{
    if(!dragging) return;
    p=clamp(p0+(e.clientY-y0)/320,0,1);
    render();
  });
  const stop=()=>{dragging=false;};
  lens.addEventListener('pointerup',stop);
  lens.addEventListener('pointercancel',stop);

  // ── arranca sola al entrar en pantalla, una vez ──
  let fired=false;
  new IntersectionObserver(es=>{
    es.forEach(en=>{ if(en.isIntersecting&&!fired){ fired=true; setTimeout(run,420); } });
  },{root:document.querySelector('.tour-container'),threshold:.55}).observe(lens);

  render();
})();

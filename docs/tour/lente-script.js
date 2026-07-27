/* Lente de escala - 5 capas. Requiere lensA..lensE y tecN. */

(function(){
  const lens=document.getElementById('lens');
  if(!lens) return;
  const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;

  // ── CONFIGURACION DE CAPAS ──────────────────────────────────
  // desde/hasta: tramo de progreso en que la capa es visible
  // z0/z1: escala al entrar y al salir. origen: punto de fuga.
  const CAPAS=[
    {id:'lensA', desde:0.00, hasta:0.28, z0:1.00, z1:3.20, origen:'60% 52%', fundido:0.06},
    {id:'lensB', desde:0.20, hasta:0.58, z0:0.90, z1:2.80, origen:'70% 45%', fundido:0.08},
    {id:'lensC', desde:0.50, hasta:0.76, z0:0.90, z1:2.60, origen:'50% 50%', fundido:0.06},
    {id:'lensD', desde:0.70, hasta:0.92, z0:0.90, z1:2.40, origen:'45% 50%', fundido:0.06},
    {id:'lensE', desde:0.86, hasta:1.01, z0:1.25, z1:2.60, origen:'50% 64%', fundido:0.06, centrar:true}
  ];

  // Anclajes de escala, en milimetros de campo de visión.
  // El unico dato duro: el cilindro de HPA mide 1 mm y el recorte de la
  // capa 3 cubre ~0,6 mm. Las capas 4 y 5 son estimaciones razonables.
  const ESCALA=[
    [0.00, 280], [0.24, 40],
    [0.50, 6],   [0.66, 0.6],
    [0.84, 0.12],[1.00, 0.03]
  ];

  const TECNICA=[
    [0.00,'Fotografía'],
    [0.20,'Macrofotografía'],
    [0.52,'Inmunohistoquímica'],
    [0.72,'Inmunofluorescencia']
  ];

  const DUR=13000;   // duración total del descenso

  // Puntos donde una capa releva a la siguiente (centro de cada solape)
  const SALTOS=[0.24, 0.54, 0.73, 0.89];

  const FRENO   = 0.72;   // cuanto se ralentiza en el salto (0-1)
  const ANTES   = 0.11;   // cuanto antes empieza a frenar
  const DESPUES = 0.05;   // cuanto tarda en recuperar

  // Ajuste fino por tramo. factor<1 va mas despacio, >1 mas rapido.
  // Util cuando una capa concreta se pasa de rapida.
  const RITMO=[
    {desde:0.18, hasta:0.48, factor:0.60}   // capa 2, la piel
  ];

  const el=id=>document.getElementById(id);
  const fovN=el('fovN'), fovU=el('fovU'), barN=el('barN'), barU=el('barU');
  const magN=el('magN'), tecN=el('tecN'), play=el('lensPlay');

  // Si falta alguna capa en el HTML, se ignora en vez de tumbar el script
  const faltan=CAPAS.filter(c=>!el(c.id)).map(c=>c.id);
  if(faltan.length){
    console.warn('[lente] faltan en el HTML: '+faltan.join(', ')+
                 '. Pega la version actualizada de lente-seccion.html.');
  }
  const ACTIVAS=CAPAS.filter(c=>el(c.id));
  if(!ACTIVAS.length) return;
  ACTIVAS.forEach(c=>{
    c.nodo=el(c.id);
    c.nodo.style.transformOrigin=c.origen;
    const m=c.origen.match(/([\d.]+)%\s+([\d.]+)%/);   // para poder centrarlo
    c.ox=m?+m[1]:50; c.oy=m?+m[2]:50;
  });

  const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
  const map=(v,a,b)=>clamp((v-a)/(b-a),0,1);
  // Velocidad de descenso en cada punto del recorrido. Vale 1 en crucero,
  // baja al acercarse a un salto y arranca y frena suave en los extremos.
  // La bajada es asimetrica: entra despacio mucho antes y recupera rapido.
  function velocidad(p){
    let v=1;
    v*= 0.30+0.70*Math.min(1, p/0.10);        // arranque
    v*= 0.30+0.70*Math.min(1, (1-p)/0.10);    // frenada final
    for(const s of SALTOS){
      const w = p<s ? ANTES : DESPUES;
      v *= 1-FRENO*Math.exp(-Math.pow((p-s)/w,2));
    }
    return Math.max(v,0.08);
  }

  // Interpolacion logaritmica entre anclajes: el zoom se percibe uniforme
  function fovEn(p){
    for(let i=0;i<ESCALA.length-1;i++){
      const [pa,fa]=ESCALA[i], [pb,fb]=ESCALA[i+1];
      if(p<=pb){
        const t=map(p,pa,pb);
        return fa*Math.pow(fb/fa,t);
      }
    }
    return ESCALA[ESCALA.length-1][1];
  }

  function fmt(mm){
    if(mm>=100) return [(mm/10).toFixed(1).replace('.',','),'cm'];
    if(mm>=1)   return [mm.toFixed(1).replace('.',','),'mm'];
    return [Math.round(mm*1000).toString(),'µm'];
  }

  let p=0, tecPrev='';
  function render(){
    ACTIVAS.forEach(c=>{
      // La primera capa no entra desde cero y la ultima no se desvanece
      const dentro = c.desde<=0 ? 1 : map(p,c.desde,c.desde+c.fundido);
      const fuera  = c.hasta>=1 ? 1 : 1-map(p,c.hasta-c.fundido,c.hasta);
      const o=Math.min(dentro,fuera);
      const k=map(p,c.desde,c.hasta);
      const z=c.z0*Math.pow(c.z1/c.z0,k);
      // Llevar el punto de fuga al centro, sin desplazar mas de lo que
      // sobresale la imagen por el borde (si no, se veria el fondo).
      let tx=0,ty=0;
      if(c.centrar){
        const tope=(z-1)/2*100;
        const suave=k*k*(3-2*k);
        tx=clamp((50-c.ox)*suave,-tope,tope);
        ty=clamp((50-c.oy)*suave,-tope,tope);
      }
      c.nodo.style.transform='translate('+tx.toFixed(2)+'%,'+ty.toFixed(2)+'%) scale('+z.toFixed(4)+')';
      c.nodo.style.opacity=o.toFixed(3);
      c.nodo.style.filter=(!reduce&&o>0&&o<1)?'blur('+((1-o)*4).toFixed(2)+'px)':'none';
    });

    const fov=fovEn(p);
    const [n,u]=fmt(fov);
    if(fovN){ fovN.textContent=n; fovU.textContent=u; }
    if(barN){ barN.textContent=n; barU.textContent=u; }
    if(magN){ magN.textContent=Math.round(280/fov); }

    if(tecN){
      let t=TECNICA[0][1];
      TECNICA.forEach(([pp,nombre])=>{ if(p>=pp) t=nombre; });
      if(t!==tecPrev){
        tecN.textContent=t; tecPrev=t;
        tecN.classList.add('cambia');
        setTimeout(()=>tecN.classList.remove('cambia'),900);
      }
    }
  }

  // Integrar 1/velocidad da el instante en que se alcanza cada progreso.
  // Se tabula una vez al arrancar y luego se consulta por biseccion.
  const N=2000, TIEMPO=new Float64Array(N+1);
  let acum=0;
  for(let i=1;i<=N;i++){
    acum += (1/N)/velocidad((i-0.5)/N);
    TIEMPO[i]=acum;
  }
  const ESCALA_T=DUR/acum;                    // normalizar a la duracion pedida
  for(let i=0;i<=N;i++) TIEMPO[i]*=ESCALA_T;
  const TOTAL=DUR;

  function progresoEn(ms){
    if(ms<=0) return 0;
    if(ms>=TOTAL) return 1;
    let lo=0,hi=N;
    while(lo<hi){ const m=(lo+hi)>>1; if(TIEMPO[m]<ms) lo=m+1; else hi=m; }
    // interpolar entre los dos puntos de la tabla
    const t0=TIEMPO[lo-1], t1=TIEMPO[lo];
    const f=(t1>t0)?(ms-t0)/(t1-t0):0;
    return (lo-1+f)/N;
  }

  let raf=null,t0=null;
  function step(ts){
    if(t0===null) t0=ts;
    const ms=ts-t0;
    p=progresoEn(ms); render();
    if(ms<TOTAL){ raf=requestAnimationFrame(step); }
    else{ p=1; render(); lens.classList.remove('is-running'); raf=null; }
  }
  function run(){
    if(raf) cancelAnimationFrame(raf);
    t0=null; p=0; lens.classList.add('is-running');
    if(reduce){ p=1; render(); lens.classList.remove('is-running'); return; }
    raf=requestAnimationFrame(step);
  }
  if(play) play.addEventListener('click',run);

  let arrastra=false,y0=0,p0=0;
  lens.addEventListener('pointerdown',e=>{
    if(raf){ cancelAnimationFrame(raf); raf=null; lens.classList.remove('is-running'); }
    arrastra=true; y0=e.clientY; p0=p; lens.setPointerCapture(e.pointerId);
  });
  lens.addEventListener('pointermove',e=>{
    if(!arrastra) return;
    p=clamp(p0+(e.clientY-y0)/560,0,1); render();
  });
  const suelta=()=>{arrastra=false;};
  lens.addEventListener('pointerup',suelta);
  lens.addEventListener('pointercancel',suelta);

  let lanzada=false;
  new IntersectionObserver(es=>{
    es.forEach(en=>{ if(en.isIntersecting&&!lanzada){ lanzada=true; setTimeout(run,420); } });
  },{root:document.querySelector('.tour-container'),threshold:.55}).observe(lens);

  render();
})();
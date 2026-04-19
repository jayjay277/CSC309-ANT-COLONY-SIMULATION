import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ACO Simulator — EkehFJ",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get help": None, "Report a bug": None, "About": None},
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');
:root {
  --bg:#080c14; --surface:#0f1623; --border:rgba(94,234,212,.15); --accent:#5eead4;
}
.stApp { background:var(--bg) !important; }
.stDeployButton { display:none !important; }
#MainMenu { visibility:hidden !important; }
footer    { visibility:hidden !important; }
section[data-testid="stSidebar"] {
  background:var(--surface) !important;
  border-right:1px solid var(--border) !important;
}
.block-container {
  padding-top:2rem !important;
  padding-left:1.2rem !important;
  padding-right:1.2rem !important;
  max-width:100% !important;
}
h1,h2,h3,h4 { font-family:'Syne',sans-serif !important; color:var(--accent) !important; }
div[data-testid="stButton"] button {
  width:100% !important; border-radius:8px !important;
  font-family:'DM Mono',monospace !important; letter-spacing:.1em !important;
  font-size:.78rem !important; font-weight:600 !important; padding:0.45rem 0.5rem !important;
}
/* button colour overrides */
div[data-testid="stButton"]:has(button[kind="secondary"]) button { 
  background:transparent !important; 
}
.btn-run  > div > button { background:rgba(34,197,94,.12)  !important; border:1.5px solid #22c55e !important; color:#22c55e !important; }
.btn-stop > div > button { background:rgba(245,158,11,.12) !important; border:1.5px solid #f59e0b !important; color:#f59e0b !important; }
.btn-reset> div > button { background:transparent          !important; border:1.5px solid #f43f5e !important; color:#f43f5e !important; }
.btn-step > div > button { background:rgba(94,234,212,.08) !important; border:1.5px solid #5eead4 !important; color:#5eead4 !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────
if "sim_cmd" not in st.session_state:
    st.session_state.sim_cmd = "run"   # run | stop | reset | step

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#0f1623,#161e2e);padding:15px 17px;'
        'border-radius:14px;border:1px solid rgba(94,234,212,.15);margin-bottom:12px">'
        '<div style="font-size:9px;color:#64748b;text-transform:uppercase;letter-spacing:.12em;'
        'margin-bottom:4px;font-family:DM Mono,monospace">Developer</div>'
        '<div style="font-size:19px;font-weight:800;color:#5eead4;font-family:Syne,sans-serif;line-height:1.2">'
        'EKEH FAVOUR<br>JUNIOR</div>'
        '<div style="margin-top:10px;border-top:1px solid rgba(255,255,255,.06);padding-top:9px;'
        'font-size:11px;color:#94a3b8;font-family:DM Mono,monospace">'
        '<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
        '<span>REG</span><strong style="color:#e2e8f0">20231390832</strong></div>'
        '<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
        '<span>DEPT</span><strong style="color:#e2e8f0">CYBERSECURITY</strong></div>'
        '<div style="display:flex;justify-content:space-between">'
        '<span>COURSE</span><strong style="color:#e2e8f0">CSC309</strong></div>'
        '</div></div>', unsafe_allow_html=True)

    st.markdown("### ⚙️ Swarm Controls")
    num_ants  = st.slider("Colony Size",      20, 300,  80, 10)
    ant_speed = st.slider("Ant Speed",         1,   8,   3,  1)
    wander    = st.slider("Wander Factor",     1,  60,  25,  1, help="Higher = more random")

    st.markdown("### 🧪 Pheromone Engine")
    trail_str = st.slider("Trail Strength",   10, 200, 100, 10)
    evap_rate = st.slider("Evaporation Rate",  1,  30,   8,  1)

    st.markdown("### 🗺️ Environment")
    obs_preset = st.selectbox("Obstacle Preset", ["None","Wall","Maze","Random"])
    obs_id     = {"None":0,"Wall":1,"Maze":2,"Random":3}[obs_preset]

    st.markdown("### 🎨 Visualisation")
    show_trails  = st.toggle("Show Pheromone Trails", value=True)
    show_heatmap = st.toggle("Heat-map Overlay",      value=False)
    trail_glow   = st.toggle("Trail Glow Effect",     value=False)

    st.markdown("---")

    # ── CONTROL BUTTONS (Streamlit-native, always visible) ──
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="btn-run">', unsafe_allow_html=True)
        if st.button("▶ RUN", key="btn_run", use_container_width=True):
            st.session_state.sim_cmd = "run"
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-stop">', unsafe_allow_html=True)
        if st.button("⏸ STOP", key="btn_stop", use_container_width=True):
            st.session_state.sim_cmd = "stop"
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="btn-step">', unsafe_allow_html=True)
        if st.button("⏭ STEP", key="btn_step", use_container_width=True):
            st.session_state.sim_cmd = "step"
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
        if st.button("↺ RESET", key="btn_reset", use_container_width=True):
            st.session_state.sim_cmd = "reset"
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<details style="background:#161e2e;border:1px solid rgba(94,234,212,.15);'
        'border-radius:12px;padding:4px 14px">'
        '<summary style="font-family:DM Mono,monospace;font-size:.78rem;color:#5eead4;'
        'padding:8px 2px;cursor:pointer">Algorithm Notes</summary>'
        '<div style="font-size:.8rem;color:#94a3b8;padding:8px 0 12px;line-height:1.65">'
        '<strong style="color:#e2e8f0">Ant Colony Optimisation (ACO)</strong><br><br>'
        '1. Agents spawn at the nest and explore stochastically.<br>'
        '2. Upon finding food, they return depositing pheromone vectors.<br>'
        '3. Shorter paths accumulate pheromone faster.<br>'
        '4. Evaporation prunes weak paths — emergent optimal routing.'
        '</div></details>', unsafe_allow_html=True)

# ── PAGE HEADER ──────────────────────────────────────────
cmd = st.session_state.sim_cmd
badge_text  = "● RUNNING" if cmd != "stop" else "○ PAUSED"
badge_color = "#22c55e"   if cmd != "stop" else "#64748b"
badge_bg    = "rgba(34,197,94,.15)" if cmd != "stop" else "rgba(100,116,139,.15)"
badge_bdr   = "#22c55e"   if cmd != "stop" else "#64748b"

st.markdown(
    f'<div style="margin-bottom:8px">'
    f'<span style="font-family:Syne,sans-serif;font-size:1.65rem;font-weight:800;color:#5eead4">'
    f'Ant Colony Optimisation</span>'
    f'&nbsp;&nbsp;<span style="display:inline-block;padding:2px 10px;border-radius:99px;'
    f'font-size:.68rem;font-family:DM Mono,monospace;letter-spacing:.08em;text-transform:uppercase;'
    f'background:{badge_bg};color:{badge_color};border:1px solid {badge_bdr}">{badge_text}</span>'
    f'</div>'
    f'<div style="font-size:.75rem;color:#64748b;font-family:DM Mono,monospace;'
    f'letter-spacing:.04em;margin-bottom:10px">'
    f'Swarm intelligence foraging simulator · CSC309 · 60 fps client-side canvas</div>',
    unsafe_allow_html=True
)

# ── cmd is consumed once — after "step" or "reset" revert to run/stop ──
# We pass cmd into JS; JS uses it once on load to set initial state.
# "reset" restarts the sim; "step" does one tick then pauses.
js_autorun  = "false" if cmd == "stop"  else "true"
js_do_reset = "true"  if cmd == "reset" else "false"
js_do_step  = "true"  if cmd == "step"  else "false"

# After a one-shot command, revert session state so next normal rerun is neutral
if cmd in ("reset", "step"):
    st.session_state.sim_cmd = "stop" if cmd == "step" else "run"

# ── HTML + JS ────────────────────────────────────────────
html_code = f"""<!DOCTYPE html>
<html>
<head>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{
  background:#080c14;
  font-family:'DM Mono',monospace;
  display:flex; flex-direction:column; align-items:center; overflow:hidden;
}}
#wrap {{
  display:flex; gap:14px; width:100%; padding:8px 10px 6px; align-items:flex-start;
}}
canvas {{
  border-radius:12px;
  border:1px solid rgba(94,234,212,.18);
  box-shadow:0 12px 40px rgba(0,0,0,.7);
  flex-shrink:0;
}}
#stats {{
  flex:1; display:flex; flex-direction:column; gap:8px;
  min-width:155px; max-width:205px;
}}
.card {{
  background:#161e2e; border:1px solid rgba(94,234,212,.15);
  border-radius:14px; padding:11px 15px;
}}
.clabel {{
  font-size:9px; color:#64748b; text-transform:uppercase;
  letter-spacing:.07em; margin-bottom:4px;
}}
.cval {{ font-size:1.2rem; color:#5eead4; line-height:1.1; }}
.csub {{ font-size:10px; color:#64748b; }}
.srow {{
  display:flex; justify-content:space-between; align-items:center;
  background:#161e2e; border:1px solid rgba(94,234,212,.15);
  border-radius:14px; padding:10px 15px;
  font-size:9px; color:#64748b; text-transform:uppercase; letter-spacing:.07em;
}}
#eff-wrap {{
  background:rgba(15,22,36,.8); border:1px solid rgba(94,234,212,.15);
  border-radius:99px; height:7px; overflow:hidden; margin-top:6px;
}}
#eff-bar {{
  height:100%; border-radius:99px;
  background:linear-gradient(90deg,#a78bfa,#5eead4);
  width:0%; transition:width .3s;
}}
</style>
</head>
<body>
<div id="wrap">
  <canvas id="c"></canvas>
  <div id="stats">
    <div class="srow">
      <span>Status</span>
      <span id="s-status" style="font-size:11px;font-weight:600;color:#22c55e">RUNNING</span>
    </div>
    <div class="card"><div class="clabel">Biomass Harvested</div>
      <div class="cval" id="s-food">0</div></div>
    <div class="card"><div class="clabel">Payload Carriers</div>
      <div class="cval"><span id="s-carry">0</span><span class="csub"> / {num_ants}</span></div></div>
    <div class="card"><div class="clabel">Rate (units / min)</div>
      <div class="cval"><span id="s-rate">0</span>
      <span class="csub" id="s-best"> best 0</span></div></div>
    <div class="card"><div class="clabel">Active Trails</div>
      <div class="cval" id="s-trails">0</div></div>
    <div class="card"><div class="clabel">Sim Ticks</div>
      <div class="cval" id="s-ticks">0</div></div>
    <div class="card">
      <div class="clabel">Carrier Efficiency
        <span id="s-eff-pct" style="color:#5eead4"> 0%</span></div>
      <div id="eff-wrap"><div id="eff-bar"></div></div>
    </div>
  </div>
</div>

<script>
const CFG = {{
  numAnts:    {num_ants},
  antSpeed:   {ant_speed},
  wander:     {wander} / 100,
  trailStr:   {trail_str},
  evapRate:   {evap_rate},
  obsPreset:  {obs_id},
  showTrails: {'true' if show_trails else 'false'},
  showHeat:   {'true' if show_heatmap else 'false'},
  trailGlow:  {'true' if trail_glow else 'false'},
  autoRun:    {js_autorun},
  doReset:    {js_do_reset},
  doStep:     {js_do_step},
}};

const canvas = document.getElementById('c');
const ctx    = canvas.getContext('2d');
let NEST, FOOD;
const NEST_R=40, FOOD_R=36, MAX_PHERO=1200;

function sizeCanvas() {{
  const wrap=document.getElementById('wrap');
  const sw=document.getElementById('stats').offsetWidth||200;
  const W=Math.max(360, wrap.clientWidth - sw - 24);
  const H=Math.round(W*0.52);
  canvas.width=W; canvas.height=H;
  NEST={{x:Math.round(W*0.12), y:Math.round(H/2)}};
  FOOD={{x:Math.round(W*0.88), y:Math.round(H/2)}};
  buildObs();
}}

let colony=[], pheromones=[], obstacles=[], heatmap={{}};
let foodCollected=0, tick=0, simRunning=CFG.autoRun;
let rateBuf=[], bestRate=0;

function rnd(a,b){{ return a+Math.random()*(b-a); }}

function buildObs() {{
  obstacles=[];
  const cx=canvas.width/2, cy=canvas.height/2;
  if(CFG.obsPreset===1){{
    for(let i=-5;i<=5;i++) obstacles.push({{x:cx,y:cy+i*38,r:18}});
  }}else if(CFG.obsPreset===2){{
    for(let i=-3;i<=3;i++) obstacles.push({{x:cx+i*50,y:cy-75,r:20}});
    for(let i=-2;i<=4;i++) obstacles.push({{x:cx-25+i*50,y:cy+75,r:20}});
  }}else if(CFG.obsPreset===3){{
    for(let i=0;i<8;i++){{
      const s=Math.sin(i*127.1)*43758.5453, t=Math.sin(i*311.7)*43758.5453;
      obstacles.push({{x:180+(Math.abs(s)%(canvas.width-360)),
                       y:60+(Math.abs(t)%(canvas.height-120)),
                       r:18+Math.abs(Math.sin(i)*20)}});
    }}
  }}
}}

function inObs(x,y){{
  for(const o of obstacles) if(Math.hypot(x-o.x,y-o.y)<o.r) return true;
  return false;
}}

function makeAnt(){{
  return {{x:NEST.x+rnd(-8,8),y:NEST.y+rnd(-8,8),
           angle:rnd(0,Math.PI*2),speed:CFG.antSpeed+rnd(0,1.5),hasFood:false}};
}}

function initSim(){{
  colony=Array.from({{length:CFG.numAnts}},makeAnt);
  pheromones=[]; heatmap={{}};
  foodCollected=0; tick=0; rateBuf=[]; bestRate=0;
}}

function stepOnce(){{
  tick++;
  pheromones=pheromones.filter(p=>{{p.life-=CFG.evapRate;return p.life>0;}});
  const now=Date.now();
  for(const ant of colony){{
    const dxF=FOOD.x-ant.x,dyF=FOOD.y-ant.y;
    const dxN=NEST.x-ant.x,dyN=NEST.y-ant.y;
    if(!ant.hasFood&&Math.hypot(dxF,dyF)<FOOD_R+4){{
      ant.hasFood=true;ant.angle=Math.atan2(dyN,dxN);continue;
    }}
    if(ant.hasFood&&Math.hypot(dxN,dyN)<NEST_R+4){{
      ant.hasFood=false;ant.angle=rnd(0,Math.PI*2);
      foodCollected++;rateBuf.push(now);continue;
    }}
    if(ant.hasFood){{
      if(Math.random()<0.18){{
        pheromones.push({{x:ant.x,y:ant.y,life:CFG.trailStr}});
        if(pheromones.length>MAX_PHERO) pheromones.shift();
      }}
      ant.angle+=(Math.atan2(dyN,dxN)-ant.angle)*0.18;
    }}else{{
      let bd=999,bp=null;
      for(const p of pheromones){{
        const d=Math.hypot(p.x-ant.x,p.y-ant.y);
        if(d<60&&d<bd){{bd=d;bp=p;}}
      }}
      if(bp) ant.angle+=(Math.atan2(FOOD.y-ant.y,FOOD.x-ant.x)-ant.angle)*0.35;
      else   ant.angle+=(Math.random()-.5)*CFG.wander*2;
    }}
    let nx=ant.x+Math.cos(ant.angle)*ant.speed;
    let ny=ant.y+Math.sin(ant.angle)*ant.speed;
    if(inObs(nx,ny)){{
      ant.angle+=Math.PI*0.5+rnd(-.4,.4);
      nx=ant.x+Math.cos(ant.angle)*ant.speed;
      ny=ant.y+Math.sin(ant.angle)*ant.speed;
    }}
    ant.x=nx;ant.y=ny;
    if(ant.x<4||ant.x>canvas.width-4) {{ant.angle=Math.PI-ant.angle;ant.x=Math.max(4,Math.min(canvas.width-4,ant.x));}}
    if(ant.y<4||ant.y>canvas.height-4){{ant.angle=-ant.angle;        ant.y=Math.max(4,Math.min(canvas.height-4,ant.y));}}
    if(CFG.showHeat){{const k=(ant.x>>4)+','+(ant.y>>4);heatmap[k]=(heatmap[k]||0)+1;}}
  }}
}}

function drawFrame(){{
  const W=canvas.width,H=canvas.height;
  ctx.fillStyle='#080c14';ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='rgba(18,24,36,1)';ctx.lineWidth=1;
  for(let x=0;x<W;x+=55){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}}
  for(let y=0;y<H;y+=55){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}}
  if(CFG.showHeat){{
    let mx=1;for(const v of Object.values(heatmap))if(v>mx)mx=v;
    for(const[k,v]of Object.entries(heatmap)){{
      const[gx,gy]=k.split(',').map(Number),t=Math.min(v/mx,1);
      ctx.fillStyle=`rgb(${{Math.round(20+t*120)}},${{Math.round(t*50)}},${{Math.round(t*80)}})`;
      ctx.fillRect(gx*16,gy*16,16,16);
    }}
  }}
  if(CFG.showTrails){{
    if(CFG.trailGlow)ctx.filter='blur(2px)';
    for(const p of pheromones){{
      const t=Math.max(0,Math.min(1,p.life/CFG.trailStr));
      ctx.fillStyle=`rgba(94,234,212,${{(t*.85).toFixed(3)}})`;
      ctx.fillRect(p.x-1,p.y-1,3,3);
    }}
    if(CFG.trailGlow)ctx.filter='none';
  }}
  for(const o of obstacles){{
    ctx.fillStyle='#1c2334';ctx.strokeStyle='#3c5070';ctx.lineWidth=2;
    ctx.beginPath();ctx.arc(o.x,o.y,o.r,0,Math.PI*2);ctx.fill();ctx.stroke();
  }}
  for(const r of[58,46,34]){{
    ctx.strokeStyle='rgba(100,60,220,0.35)';ctx.lineWidth=1;
    ctx.beginPath();ctx.arc(NEST.x,NEST.y,r,0,Math.PI*2);ctx.stroke();
  }}
  ctx.fillStyle='rgb(100,60,220)';
  ctx.beginPath();ctx.arc(NEST.x,NEST.y,NEST_R,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='rgba(200,190,255,.9)';ctx.font='bold 13px DM Mono,monospace';
  ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('N',NEST.x,NEST.y);
  for(const r of[52,40,28]){{
    ctx.strokeStyle='rgba(240,60,80,0.35)';ctx.lineWidth=1;
    ctx.beginPath();ctx.arc(FOOD.x,FOOD.y,r,0,Math.PI*2);ctx.stroke();
  }}
  ctx.fillStyle='rgb(240,60,80)';
  ctx.beginPath();ctx.arc(FOOD.x,FOOD.y,FOOD_R,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='rgba(255,220,200,.9)';ctx.font='bold 13px DM Mono,monospace';
  ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('F',FOOD.x,FOOD.y);
  for(const ant of colony){{
    const ca=Math.cos(ant.angle),sa=Math.sin(ant.angle);
    ctx.fillStyle=ant.hasFood?'#f97316':'#cbd5e1';
    ctx.beginPath();ctx.ellipse(ant.x-ca*6,ant.y-sa*6,3,2,ant.angle,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.ellipse(ant.x,ant.y,5,3,ant.angle,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.ellipse(ant.x+ca*7,ant.y+sa*7,3,3,ant.angle,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='rgba(148,163,184,.55)';ctx.lineWidth=1;
    for(let i=-1;i<=1;i++){{
      const lx=ant.x-sa*(i*4),ly=ant.y+ca*(i*4);
      ctx.beginPath();ctx.moveTo(lx,ly);ctx.lineTo(lx-sa*7-ca*3,ly+ca*7-sa*3);
      ctx.moveTo(lx,ly);ctx.lineTo(lx+sa*7-ca*3,ly-ca*7-sa*3);ctx.stroke();
    }}
    if(ant.hasFood){{ctx.fillStyle='#fb923c';ctx.beginPath();ctx.arc(ant.x,ant.y,3,0,Math.PI*2);ctx.fill();}}
  }}
  const lx=W-150,ly=H-65;
  ctx.fillStyle='rgba(12,18,30,.9)';ctx.strokeStyle='rgba(40,55,80,1)';ctx.lineWidth=1;
  ctx.beginPath();ctx.roundRect(lx-8,ly-8,148,66,8);ctx.fill();ctx.stroke();
  ctx.fillStyle='rgb(100,60,220)';ctx.beginPath();ctx.arc(lx+6,ly+8,6,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='rgba(180,170,240,.9)';ctx.font='11px DM Mono,monospace';ctx.textAlign='left';ctx.textBaseline='middle';
  ctx.fillText('Nest',lx+16,ly+8);
  ctx.fillStyle='rgb(240,60,80)';ctx.beginPath();ctx.arc(lx+6,ly+26,6,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='rgba(255,200,190,.9)';ctx.fillText('Food',lx+16,ly+26);
  ctx.fillStyle='rgba(94,234,212,.8)';ctx.fillRect(lx,ly+42,12,5);
  ctx.fillStyle='rgba(160,240,220,.9)';ctx.fillText('Trail',lx+16,ly+44);
  ctx.fillStyle=simRunning?'#22c55e':'#64748b';
  ctx.beginPath();ctx.arc(10,10,5,0,Math.PI*2);ctx.fill();
}}

let frameCount=0;
function updateStats(){{
  const now=Date.now();
  rateBuf=rateBuf.filter(t=>now-t<60000);
  const rate=rateBuf.length;
  if(rate>bestRate)bestRate=rate;
  const carrying=colony.filter(a=>a.hasFood).length;
  const eff=Math.round(carrying/Math.max(1,colony.length)*100);
  document.getElementById('s-food').textContent   =foodCollected;
  document.getElementById('s-carry').textContent  =carrying;
  document.getElementById('s-rate').textContent   =rate;
  document.getElementById('s-best').textContent   =' best '+bestRate;
  document.getElementById('s-trails').textContent =pheromones.length;
  document.getElementById('s-ticks').textContent  =tick;
  document.getElementById('s-eff-pct').textContent=' '+eff+'%';
  document.getElementById('eff-bar').style.width  =eff+'%';
  const el=document.getElementById('s-status');
  el.textContent=simRunning?'RUNNING':'PAUSED';
  el.style.color=simRunning?'#22c55e':'#64748b';
}}

function loop(){{
  if(simRunning) stepOnce();
  drawFrame();
  frameCount++;
  if(frameCount%6===0) updateStats();
  requestAnimationFrame(loop);
}}

// ── BOOT — honour one-shot commands from Python ──────────
sizeCanvas();
if(CFG.doReset){{
  initSim();
}} else {{
  initSim();   // always init fresh on page/rerun load
}}
if(CFG.doStep){{
  simRunning=false;
  stepOnce();
}}
simRunning = CFG.doReset ? true : (CFG.doStep ? false : CFG.autoRun);
updateStats();
loop();
</script>
</body>
</html>
"""

components.html(html_code, height=660, scrolling=False)

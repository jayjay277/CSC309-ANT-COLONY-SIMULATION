import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ACO Simulator — EkehFJ",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get help": None, "Report a bug": None, "About": None},
)

# Hide ALL Streamlit chrome so the HTML component is the entire page
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

/* Hide every piece of Streamlit UI */
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebarCollapsedControl"],
.stDeployButton { display:none !important; visibility:hidden !important; }

/* Collapse sidebar completely */
section[data-testid="stSidebar"] { display:none !important; }

/* Remove all page padding so our component is edge-to-edge */
.block-container {
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
}
.stApp { background:#080c14 !important; }
[data-testid="stVerticalBlock"] { gap:0 !important; padding:0 !important; }
</style>
""", unsafe_allow_html=True)

# Everything — controls, canvas, stats — lives inside the HTML component.
# This completely sidesteps Streamlit layout issues on mobile.
html_code = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg:      #080c14;
  --surf:    #0f1623;
  --surf2:   #161e2e;
  --border:  rgba(94,234,212,.15);
  --accent:  #5eead4;
  --purple:  #a78bfa;
  --green:   #22c55e;
  --amber:   #f59e0b;
  --red:     #f43f5e;
  --muted:   #64748b;
}

* { box-sizing:border-box; margin:0; padding:0; }

html, body {
  width:100%; height:100%;
  background:var(--bg);
  font-family:'DM Mono',monospace;
  color:#e2e8f0;
  overflow-x:hidden;
}

/* ═══════════════════════════════════════
   TOP HEADER BAR
═══════════════════════════════════════ */
#header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:10px 14px 8px;
  border-bottom:1px solid var(--border);
  flex-wrap:wrap;
  gap:6px;
}
#header-left h1 {
  font-family:'Syne',sans-serif;
  font-size:clamp(1rem,3.5vw,1.5rem);
  font-weight:800;
  color:var(--accent);
  line-height:1;
}
#header-left p {
  font-size:clamp(.58rem,.9vw,.7rem);
  color:var(--muted);
  margin-top:3px;
  letter-spacing:.03em;
}
#badge {
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 10px; border-radius:99px;
  font-size:.65rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
  background:rgba(34,197,94,.15); color:var(--green); border:1px solid var(--green);
  white-space:nowrap;
}
#dev-chip {
  background:var(--surf2);
  border:1px solid var(--border);
  border-radius:10px;
  padding:5px 12px;
  font-size:.65rem;
  color:#94a3b8;
  line-height:1.5;
  white-space:nowrap;
}
#dev-chip strong { color:#e2e8f0; }

/* ═══════════════════════════════════════
   MAIN BODY  (canvas + stats side by side on desktop,
               stacked on mobile)
═══════════════════════════════════════ */
#body {
  display:flex;
  flex-direction:row;
  gap:12px;
  padding:10px 12px 8px;
  align-items:flex-start;
}
#canvas-wrap { flex:1; min-width:0; }
canvas {
  width:100%;
  height:auto;
  border-radius:12px;
  border:1px solid rgba(94,234,212,.2);
  box-shadow:0 8px 32px rgba(0,0,0,.6);
  display:block;
}
#stats-panel {
  display:flex;
  flex-direction:column;
  gap:7px;
  width:190px;
  flex-shrink:0;
}

/* ═══════════════════════════════════════
   CONTROLS BAR
═══════════════════════════════════════ */
#controls {
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  padding:0 12px 10px;
  align-items:flex-start;
}
#ctrl-left {
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  flex:1;
}

/* Buttons */
.btn {
  padding:7px 14px;
  border-radius:8px;
  font-family:'DM Mono',monospace;
  font-size:.75rem;
  font-weight:600;
  letter-spacing:.08em;
  cursor:pointer;
  border:1.5px solid;
  touch-action:manipulation;
  white-space:nowrap;
  transition:filter .15s;
}
.btn:hover, .btn:active { filter:brightness(1.3); }
.btn-run   { background:rgba(34,197,94,.12);  border-color:var(--green); color:var(--green); }
.btn-stop  { background:rgba(245,158,11,.12); border-color:var(--amber); color:var(--amber); }
.btn-step  { background:rgba(94,234,212,.08); border-color:var(--accent);color:var(--accent); }
.btn-reset { background:transparent;          border-color:var(--red);   color:var(--red); }

/* Slider group */
.ctrl-group {
  background:var(--surf2);
  border:1px solid var(--border);
  border-radius:12px;
  padding:8px 12px;
  display:flex;
  flex-wrap:wrap;
  gap:6px 18px;
  align-items:center;
  flex:1;
}
.ctrl-item {
  display:flex;
  align-items:center;
  gap:6px;
  white-space:nowrap;
}
.ctrl-item label {
  font-size:.65rem;
  color:var(--muted);
  text-transform:uppercase;
  letter-spacing:.06em;
  min-width:60px;
}
.ctrl-item input[type=range] {
  width:90px;
  accent-color:var(--accent);
  cursor:pointer;
}
.ctrl-item .val {
  font-size:.7rem;
  color:var(--accent);
  min-width:28px;
  text-align:right;
}

/* Speed radio */
.speed-group { display:flex; gap:4px; flex-wrap:wrap; }
.speed-btn {
  padding:3px 9px;
  border-radius:6px;
  font-size:.65rem;
  font-weight:600;
  cursor:pointer;
  border:1.5px solid var(--border);
  color:var(--muted);
  background:transparent;
  touch-action:manipulation;
  transition:all .15s;
  font-family:'DM Mono',monospace;
  letter-spacing:.05em;
}
.speed-btn.active {
  border-color:var(--accent);
  color:var(--accent);
  background:rgba(94,234,212,.1);
}

/* Toggle */
.toggle-group { display:flex; flex-wrap:wrap; gap:6px; align-items:center; }
.tog-item { display:flex; align-items:center; gap:5px; cursor:pointer; }
.tog-item label { font-size:.65rem; color:var(--muted); cursor:pointer; text-transform:uppercase; letter-spacing:.05em; }
.tog-item input[type=checkbox] { accent-color:var(--accent); width:14px; height:14px; cursor:pointer; }

/* Select */
select {
  background:var(--surf); border:1px solid var(--border);
  color:#e2e8f0; border-radius:6px;
  font-family:'DM Mono',monospace; font-size:.65rem;
  padding:3px 7px; cursor:pointer;
}

/* ═══════════════════════════════════════
   STATS CARDS
═══════════════════════════════════════ */
.card {
  background:var(--surf2);
  border:1px solid var(--border);
  border-radius:12px;
  padding:9px 13px;
}
.clabel {
  font-size:8px; color:var(--muted);
  text-transform:uppercase; letter-spacing:.07em; margin-bottom:3px;
}
.cval  { font-size:1.1rem; color:var(--accent); line-height:1.1; font-weight:500; }
.csub  { font-size:10px; color:var(--muted); }
.srow  {
  display:flex; justify-content:space-between; align-items:center;
  background:var(--surf2); border:1px solid var(--border);
  border-radius:12px; padding:9px 13px;
  font-size:8px; color:var(--muted);
  text-transform:uppercase; letter-spacing:.07em;
}
#eff-wrap {
  background:rgba(15,22,36,.8); border:1px solid var(--border);
  border-radius:99px; height:6px; overflow:hidden; margin-top:5px;
}
#eff-bar {
  height:100%; border-radius:99px;
  background:linear-gradient(90deg,var(--purple),var(--accent));
  width:0%; transition:width .3s;
}

/* ═══════════════════════════════════════
   MOBILE  ≤ 640px
═══════════════════════════════════════ */
@media (max-width:640px) {
  #body {
    flex-direction:column;
    padding:8px 8px 4px;
    gap:8px;
  }
  #stats-panel {
    width:100%;
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:6px;
  }
  .srow    { grid-column:1/-1; }
  #eff-card{ grid-column:1/-1; }
  .cval    { font-size:.95rem !important; }

  #controls { padding:0 8px 8px; gap:6px; }
  .ctrl-group { gap:5px 12px; padding:7px 10px; }
  .ctrl-item input[type=range] { width:70px; }
  #dev-chip { display:none; } /* hide on tiny screens, already in header left */
}
</style>
</head>
<body>

<!-- ═══ HEADER ═══════════════════════════════════════════ -->
<div id="header">
  <div id="header-left">
    <h1>Ant Colony Optimisation &nbsp;<span id="badge">● RUNNING</span></h1>
    <p>Swarm intelligence foraging simulator &middot; CSC309 &middot; Speed: <span id="spd-label" style="color:var(--accent)">Normal</span></p>
  </div>
  <div id="dev-chip">
    <strong>EKEH FAVOUR JUNIOR</strong><br>
    REG <strong>20231390832</strong> &nbsp;|&nbsp; DEPT <strong>CYBERSECURITY</strong> &nbsp;|&nbsp; CSC309
  </div>
</div>

<!-- ═══ BODY: CANVAS + STATS ═══════════════════════════════ -->
<div id="body">
  <div id="canvas-wrap">
    <canvas id="c"></canvas>
  </div>
  <div id="stats-panel">
    <div class="srow">
      <span>Status</span>
      <span id="s-status" style="font-size:11px;font-weight:600;color:var(--green)">RUNNING</span>
    </div>
    <div class="card">
      <div class="clabel">Biomass Harvested</div>
      <div class="cval" id="s-food">0</div>
    </div>
    <div class="card">
      <div class="clabel">Payload Carriers</div>
      <div class="cval"><span id="s-carry">0</span><span class="csub" id="s-total"> / 80</span></div>
    </div>
    <div class="card">
      <div class="clabel">Rate (units / min)</div>
      <div class="cval"><span id="s-rate">0</span><span class="csub" id="s-best"> best 0</span></div>
    </div>
    <div class="card">
      <div class="clabel">Active Trails</div>
      <div class="cval" id="s-trails">0</div>
    </div>
    <div class="card">
      <div class="clabel">Sim Ticks</div>
      <div class="cval" id="s-ticks">0</div>
    </div>
    <div class="card" id="eff-card">
      <div class="clabel">Carrier Efficiency <span id="s-eff-pct" style="color:var(--accent)">0%</span></div>
      <div id="eff-wrap"><div id="eff-bar"></div></div>
    </div>
  </div>
</div>

<!-- ═══ CONTROLS ════════════════════════════════════════════ -->
<div id="controls">

  <!-- Action buttons -->
  <button class="btn btn-run"   onclick="startSim()">▶ RUN</button>
  <button class="btn btn-stop"  onclick="stopSim()">⏸ STOP</button>
  <button class="btn btn-step"  onclick="stepBtn()">⏭ STEP</button>
  <button class="btn btn-reset" onclick="resetSim()">↺ RESET</button>

  <!-- Settings group -->
  <div class="ctrl-group">

    <!-- Colony size -->
    <div class="ctrl-item">
      <label>Colony</label>
      <input type="range" id="r-ants" min="20" max="300" step="10" value="80"
             oninput="CFG.numAnts=+this.value; document.getElementById('v-ants').textContent=this.value; document.getElementById('s-total').textContent=' / '+this.value; resetSim()">
      <span class="val" id="v-ants">80</span>
    </div>

    <!-- Speed radio -->
    <div class="ctrl-item">
      <label>Speed</label>
      <div class="speed-group" id="speed-group">
        <button class="speed-btn"        onclick="setSpeed('Slow',1.5,this)">Slow</button>
        <button class="speed-btn active" onclick="setSpeed('Normal',3.0,this)">Normal</button>
        <button class="speed-btn"        onclick="setSpeed('Fast',5.0,this)">Fast</button>
        <button class="speed-btn"        onclick="setSpeed('Turbo',8.0,this)">Turbo</button>
      </div>
    </div>

    <!-- Wander -->
    <div class="ctrl-item">
      <label>Wander</label>
      <input type="range" id="r-wander" min="1" max="60" value="25"
             oninput="CFG.wander=+this.value/100; document.getElementById('v-wander').textContent=this.value">
      <span class="val" id="v-wander">25</span>
    </div>

    <!-- Trail strength -->
    <div class="ctrl-item">
      <label>Trail Str.</label>
      <input type="range" id="r-trail" min="10" max="200" step="10" value="100"
             oninput="CFG.trailStr=+this.value; document.getElementById('v-trail').textContent=this.value">
      <span class="val" id="v-trail">100</span>
    </div>

    <!-- Evaporation -->
    <div class="ctrl-item">
      <label>Evap.</label>
      <input type="range" id="r-evap" min="1" max="50" value="8"
             oninput="CFG.evapRate=+this.value/10; document.getElementById('v-evap').textContent=(+this.value/10).toFixed(1)">
      <span class="val" id="v-evap">0.8</span>
    </div>

    <!-- Obstacles -->
    <div class="ctrl-item">
      <label>Obstacles</label>
      <select onchange="CFG.obsPreset=+this.value; buildObs()">
        <option value="0">None</option>
        <option value="1">Wall</option>
        <option value="2">Maze</option>
        <option value="3">Random</option>
      </select>
    </div>

    <!-- Toggles -->
    <div class="toggle-group">
      <div class="tog-item">
        <input type="checkbox" id="tog-trails" checked onchange="CFG.showTrails=this.checked">
        <label for="tog-trails">Trails</label>
      </div>
      <div class="tog-item">
        <input type="checkbox" id="tog-heat" onchange="CFG.showHeat=this.checked">
        <label for="tog-heat">Heatmap</label>
      </div>
      <div class="tog-item">
        <input type="checkbox" id="tog-glow" onchange="CFG.trailGlow=this.checked">
        <label for="tog-glow">Glow</label>
      </div>
    </div>

  </div><!-- /ctrl-group -->
</div><!-- /controls -->

<!-- ═══ JAVASCRIPT ══════════════════════════════════════════ -->
<script>
const canvas = document.getElementById('c');
const ctx    = canvas.getContext('2d');

let NEST, FOOD;
const NEST_R=40, FOOD_R=36, MAX_PHERO=1500;

// Live config — mutated directly by controls
const CFG = {
  numAnts:    80,
  antSpeed:   3.0,
  wander:     0.25,
  trailStr:   100,
  evapRate:   0.8,
  obsPreset:  0,
  showTrails: true,
  showHeat:   false,
  trailGlow:  false,
};

// ── Canvas sizing ──────────────────────────────────────────
function sizeCanvas() {
  const wrap = document.getElementById('canvas-wrap');
  const W    = wrap.clientWidth;
  const H    = Math.round(W * 0.58);
  canvas.width  = W;
  canvas.height = H;
  NEST = { x: Math.round(W * 0.12), y: Math.round(H / 2) };
  FOOD = { x: Math.round(W * 0.88), y: Math.round(H / 2) };
  buildObs();
}

// ── State ──────────────────────────────────────────────────
let colony=[], pheromones=[], obstacles=[], heatmap={};
let foodCollected=0, tick=0, simRunning=true;
let rateBuf=[], bestRate=0;

function rnd(a,b) { return a + Math.random()*(b-a); }

// ── Obstacles ──────────────────────────────────────────────
function buildObs() {
  obstacles = [];
  const cx=canvas.width/2, cy=canvas.height/2;
  if(CFG.obsPreset===1) {
    for(let i=-5;i<=5;i++) obstacles.push({x:cx,y:cy+i*38,r:18});
  } else if(CFG.obsPreset===2) {
    for(let i=-3;i<=3;i++) obstacles.push({x:cx+i*50,y:cy-75,r:20});
    for(let i=-2;i<=4;i++) obstacles.push({x:cx-25+i*50,y:cy+75,r:20});
  } else if(CFG.obsPreset===3) {
    for(let i=0;i<8;i++) {
      const s=Math.sin(i*127.1)*43758.5453, t=Math.sin(i*311.7)*43758.5453;
      obstacles.push({
        x:180+(Math.abs(s)%(canvas.width-360)),
        y:60+(Math.abs(t)%(canvas.height-120)),
        r:18+Math.abs(Math.sin(i)*20)
      });
    }
  }
}

function inObs(x,y) {
  for(const o of obstacles) if(Math.hypot(x-o.x,y-o.y)<o.r) return true;
  return false;
}

// ── Ant ────────────────────────────────────────────────────
function makeAnt() {
  return {
    x: NEST.x+rnd(-8,8), y: NEST.y+rnd(-8,8),
    angle: rnd(0,Math.PI*2),
    speed: CFG.antSpeed + rnd(0, CFG.antSpeed*0.3),
    hasFood: false
  };
}

// ── Sim control ────────────────────────────────────────────
function initSim() {
  colony = Array.from({length:CFG.numAnts}, makeAnt);
  pheromones=[]; heatmap={};
  foodCollected=0; tick=0; rateBuf=[]; bestRate=0;
}
function startSim() { simRunning=true;  refreshBadge(); }
function stopSim()  { simRunning=false; refreshBadge(); }
function resetSim() { initSim(); simRunning=true; refreshBadge(); }
function stepBtn()  { simRunning=false; stepOnce(); refreshBadge(); }

function setSpeed(label, val, el) {
  CFG.antSpeed = val;
  document.getElementById('spd-label').textContent = label;
  document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  // update each ant's speed proportionally
  colony.forEach(a => a.speed = val + rnd(0, val*0.3));
}

function refreshBadge() {
  const badge = document.getElementById('badge');
  const running = simRunning;
  badge.textContent    = running ? '● RUNNING' : '○ PAUSED';
  badge.style.background   = running ? 'rgba(34,197,94,.15)' : 'rgba(100,116,139,.15)';
  badge.style.color        = running ? '#22c55e' : '#64748b';
  badge.style.borderColor  = running ? '#22c55e' : '#64748b';
}

// ── Physics ────────────────────────────────────────────────
function stepOnce() {
  tick++;
  pheromones = pheromones.filter(p => { p.life -= CFG.evapRate; return p.life > 0; });
  const now = Date.now();

  for(const ant of colony) {
    const dxF=FOOD.x-ant.x, dyF=FOOD.y-ant.y;
    const dxN=NEST.x-ant.x, dyN=NEST.y-ant.y;

    if(!ant.hasFood && Math.hypot(dxF,dyF) < FOOD_R+4) {
      ant.hasFood=true; ant.angle=Math.atan2(dyN,dxN); continue;
    }
    if(ant.hasFood && Math.hypot(dxN,dyN) < NEST_R+4) {
      ant.hasFood=false; ant.angle=rnd(0,Math.PI*2);
      foodCollected++; rateBuf.push(now); continue;
    }

    if(ant.hasFood) {
      if(Math.random()<0.18) {
        pheromones.push({x:ant.x, y:ant.y, life:CFG.trailStr});
        if(pheromones.length > MAX_PHERO) pheromones.shift();
      }
      ant.angle += (Math.atan2(dyN,dxN) - ant.angle) * 0.18;
    } else {
      let bd=999, bp=null;
      for(const p of pheromones) {
        const d=Math.hypot(p.x-ant.x, p.y-ant.y);
        if(d<60 && d<bd) { bd=d; bp=p; }
      }
      if(bp) ant.angle += (Math.atan2(FOOD.y-ant.y,FOOD.x-ant.x) - ant.angle) * 0.35;
      else   ant.angle += (Math.random()-.5) * CFG.wander * 2;
    }

    let nx = ant.x + Math.cos(ant.angle)*ant.speed;
    let ny = ant.y + Math.sin(ant.angle)*ant.speed;
    if(inObs(nx,ny)) {
      ant.angle += Math.PI*0.5 + rnd(-.4,.4);
      nx = ant.x + Math.cos(ant.angle)*ant.speed;
      ny = ant.y + Math.sin(ant.angle)*ant.speed;
    }
    ant.x=nx; ant.y=ny;
    if(ant.x<4||ant.x>canvas.width-4)  { ant.angle=Math.PI-ant.angle; ant.x=Math.max(4,Math.min(canvas.width-4,ant.x)); }
    if(ant.y<4||ant.y>canvas.height-4) { ant.angle=-ant.angle;         ant.y=Math.max(4,Math.min(canvas.height-4,ant.y)); }
    if(CFG.showHeat) { const k=(ant.x>>4)+','+(ant.y>>4); heatmap[k]=(heatmap[k]||0)+1; }
  }
}

// ── Ant sprite ─────────────────────────────────────────────
function drawAnt(x, y, angle, hasFood) {
  const sc = Math.max(0.5, Math.min(1.1, canvas.width / 800));
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.scale(sc, sc);

  const bc = hasFood ? '#fb923c' : '#cbd5e1';
  const lc = hasFood ? 'rgba(251,146,60,.5)' : 'rgba(148,163,184,.5)';

  // 6 legs
  ctx.strokeStyle=lc; ctx.lineWidth=0.8;
  const legs = [
    {bx:4,by:0,lx:10,ly:-6},{bx:0,by:0,lx:8,ly:-7},{bx:-4,by:0,lx:9,ly:-5},
    {bx:4,by:0,lx:10,ly:6}, {bx:0,by:0,lx:8,ly:7}, {bx:-4,by:0,lx:9,ly:5},
  ];
  for(const l of legs) {
    ctx.beginPath();
    ctx.moveTo(l.bx, l.by);
    ctx.lineTo((l.bx+l.lx)/2+(l.ly>0?2:-2), (l.by+l.ly)/2);
    ctx.lineTo(l.lx, l.ly);
    ctx.stroke();
  }

  ctx.fillStyle = bc;
  ctx.beginPath(); ctx.ellipse(-6, 0, 5, 3.5, 0, 0, Math.PI*2); ctx.fill(); // abdomen
  ctx.beginPath(); ctx.ellipse( 0, 0, 3, 2.5, 0, 0, Math.PI*2); ctx.fill(); // thorax
  ctx.beginPath(); ctx.ellipse( 6, 0, 3.5, 3, 0, 0, Math.PI*2); ctx.fill(); // head

  ctx.strokeStyle=lc; ctx.lineWidth=0.7;
  ctx.beginPath(); ctx.moveTo(8,-1); ctx.lineTo(13,-5);
  ctx.moveTo(8,1);  ctx.lineTo(13, 5); ctx.stroke(); // antennae

  if(hasFood) {
    ctx.fillStyle='#fbbf24';
    ctx.beginPath(); ctx.arc(-6,0,3,0,Math.PI*2); ctx.fill();
  }
  ctx.restore();
}

// ── Draw frame ─────────────────────────────────────────────
function drawFrame() {
  const W=canvas.width, H=canvas.height;
  ctx.fillStyle='#080c14'; ctx.fillRect(0,0,W,H);

  // grid
  ctx.strokeStyle='rgba(18,24,36,1)'; ctx.lineWidth=1;
  for(let x=0;x<W;x+=55) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
  for(let y=0;y<H;y+=55) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }

  // heatmap
  if(CFG.showHeat) {
    let mx=1; for(const v of Object.values(heatmap)) if(v>mx) mx=v;
    for(const [k,v] of Object.entries(heatmap)) {
      const [gx,gy]=k.split(',').map(Number), t=Math.min(v/mx,1);
      ctx.fillStyle=`rgb(${Math.round(20+t*120)},${Math.round(t*50)},${Math.round(t*80)})`;
      ctx.fillRect(gx*16,gy*16,16,16);
    }
  }

  // trails
  if(CFG.showTrails) {
    if(CFG.trailGlow) ctx.filter='blur(2px)';
    for(const p of pheromones) {
      const t=Math.max(0,Math.min(1,p.life/CFG.trailStr));
      ctx.fillStyle=`rgba(94,234,212,${(t*.85).toFixed(3)})`;
      ctx.fillRect(p.x-1,p.y-1,3,3);
    }
    if(CFG.trailGlow) ctx.filter='none';
  }

  // obstacles
  for(const o of obstacles) {
    ctx.fillStyle='#1c2334'; ctx.strokeStyle='#3c5070'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.arc(o.x,o.y,o.r,0,Math.PI*2); ctx.fill(); ctx.stroke();
  }

  // nest
  for(const r of [58,46,34]) {
    ctx.strokeStyle='rgba(100,60,220,0.35)'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.arc(NEST.x,NEST.y,r,0,Math.PI*2); ctx.stroke();
  }
  ctx.fillStyle='rgb(100,60,220)';
  ctx.beginPath(); ctx.arc(NEST.x,NEST.y,NEST_R,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='rgba(200,190,255,.9)';
  ctx.font=`bold ${Math.round(13*canvas.width/900)}px DM Mono,monospace`;
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('N',NEST.x,NEST.y);

  // food
  for(const r of [52,40,28]) {
    ctx.strokeStyle='rgba(240,60,80,0.35)'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.arc(FOOD.x,FOOD.y,r,0,Math.PI*2); ctx.stroke();
  }
  ctx.fillStyle='rgb(240,60,80)';
  ctx.beginPath(); ctx.arc(FOOD.x,FOOD.y,FOOD_R,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='rgba(255,220,200,.9)';
  ctx.font=`bold ${Math.round(13*canvas.width/900)}px DM Mono,monospace`;
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('F',FOOD.x,FOOD.y);

  // ants
  for(const ant of colony) drawAnt(ant.x,ant.y,ant.angle,ant.hasFood);

  // legend
  const fs=Math.max(9,Math.round(11*canvas.width/900));
  const lx=W-152, ly=H-68;
  ctx.fillStyle='rgba(12,18,30,.92)'; ctx.strokeStyle='rgba(40,55,80,1)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.roundRect(lx-6,ly-6,150,66,8); ctx.fill(); ctx.stroke();
  ctx.font=`${fs}px DM Mono,monospace`; ctx.textAlign='left'; ctx.textBaseline='middle';
  ctx.fillStyle='rgb(100,60,220)';      ctx.beginPath(); ctx.arc(lx+5,ly+8,5,0,Math.PI*2);  ctx.fill();
  ctx.fillStyle='rgba(180,170,240,.9)'; ctx.fillText('Nest', lx+14,ly+8);
  ctx.fillStyle='rgb(240,60,80)';       ctx.beginPath(); ctx.arc(lx+5,ly+27,5,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='rgba(255,200,190,.9)'; ctx.fillText('Food', lx+14,ly+27);
  ctx.fillStyle='rgba(94,234,212,.8)';  ctx.fillRect(lx,ly+43,10,4);
  ctx.fillStyle='rgba(160,240,220,.9)'; ctx.fillText('Trail',lx+14,ly+45);

  // status dot
  ctx.fillStyle = simRunning ? '#22c55e' : '#64748b';
  ctx.beginPath(); ctx.arc(10,10,5,0,Math.PI*2); ctx.fill();
}

// ── Stats update ───────────────────────────────────────────
let frameCount=0;
function updateStats() {
  const now=Date.now();
  rateBuf=rateBuf.filter(t=>now-t<60000);
  const rate=rateBuf.length;
  if(rate>bestRate) bestRate=rate;
  const carrying=colony.filter(a=>a.hasFood).length;
  const eff=Math.round(carrying/Math.max(1,colony.length)*100);
  document.getElementById('s-food').textContent   =foodCollected;
  document.getElementById('s-carry').textContent  =carrying;
  document.getElementById('s-rate').textContent   =rate;
  document.getElementById('s-best').textContent   =' best '+bestRate;
  document.getElementById('s-trails').textContent =pheromones.length;
  document.getElementById('s-ticks').textContent  =tick;
  document.getElementById('s-eff-pct').textContent=eff+'%';
  document.getElementById('eff-bar').style.width  =eff+'%';
  const el=document.getElementById('s-status');
  el.textContent=simRunning?'RUNNING':'PAUSED';
  el.style.color=simRunning?'#22c55e':'#64748b';
}

// ── Loop ───────────────────────────────────────────────────
function loop() {
  if(simRunning) stepOnce();
  drawFrame();
  frameCount++;
  if(frameCount%6===0) updateStats();
  requestAnimationFrame(loop);
}

// ── Resize ─────────────────────────────────────────────────
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => { sizeCanvas(); }, 120);
});

// ── Boot ───────────────────────────────────────────────────
sizeCanvas();
initSim();
loop();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)

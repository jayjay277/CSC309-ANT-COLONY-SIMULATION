import streamlit as st
import math
import random
import time
from PIL import Image, ImageDraw, ImageFilter

# ─────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ACO Simulator — EkehFJ",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get help": None, "Report a bug": None, "About": None},
)

# ─────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:      #080c14;
  --surface: #0f1623;
  --surf2:   #161e2e;
  --border:  rgba(94,234,212,.15);
  --accent:  #5eead4;
  --accent3: #a78bfa;
  --danger:  #f43f5e;
  --green:   #22c55e;
  --amber:   #f59e0b;
  --muted:   #64748b;
  --radius:  14px;
}

.stApp { background: var(--bg) !important; }
.stDeployButton { display: none !important; }
#MainMenu       { visibility: hidden !important; }
footer          { visibility: hidden !important; }

section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}

.block-container {
  padding-top: 3.5rem !important;
  padding-left: 1.2rem !important;
  padding-right: 1.2rem !important;
  max-width: 100% !important;
}

h1,h2,h3,h4 { font-family:'Syne',sans-serif !important; color:var(--accent) !important; }

div[data-testid="stButton"] button {
  width: 100% !important;
  border-radius: 8px !important;
  font-family: 'DM Mono', monospace !important;
  letter-spacing: .1em !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
  transition: all .2s !important;
  padding: 0.45rem 0.5rem !important;
}

.btn-reset button {
  background: transparent !important;
  border: 1.5px solid #f43f5e !important;
  color: #f43f5e !important;
}
.btn-reset button:hover {
  background: rgba(244,63,94,.12) !important;
  box-shadow: 0 0 14px rgba(244,63,94,.3) !important;
}
.btn-run button {
  background: rgba(34,197,94,.12) !important;
  border: 1.5px solid #22c55e !important;
  color: #22c55e !important;
}
.btn-run button:hover {
  background: rgba(34,197,94,.22) !important;
  box-shadow: 0 0 14px rgba(34,197,94,.35) !important;
}
.btn-stop button {
  background: rgba(245,158,11,.12) !important;
  border: 1.5px solid #f59e0b !important;
  color: #f59e0b !important;
}
.btn-stop button:hover {
  background: rgba(245,158,11,.22) !important;
  box-shadow: 0 0 14px rgba(245,158,11,.35) !important;
}

[data-testid="stImage"] img {
  border-radius: 12px !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 16px 48px rgba(0,0,0,.6) !important;
  width: 100% !important;
  height: auto !important;
}

.eff-bar-wrap {
  background: rgba(15,22,36,.8);
  border: 1px solid var(--border);
  border-radius: 99px;
  height: 7px;
  overflow: hidden;
  margin: 4px 0 0;
}
.eff-bar-fill {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--accent3), var(--accent));
}

.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 99px;
  font-size: .68rem;
  font-family: 'DM Mono', monospace;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.badge-run  { background:rgba(34,197,94,.15);  color:#22c55e; border:1px solid #22c55e; }
.badge-idle { background:rgba(100,116,139,.15); color:var(--muted); border:1px solid var(--muted); }

.stat-panel { display:flex; flex-direction:column; gap:8px; }
details summary::-webkit-details-marker { display:none; }

@media (max-width:900px) {
  .block-container { padding-left:.5rem !important; padding-right:.5rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  CANVAS CONSTANTS
# ─────────────────────────────────────────
CANVAS_W  = 1100
CANVAS_H  = 560
NEST_POS  = (int(CANVAS_W * 0.12), CANVAS_H // 2)
FOOD_POS  = (int(CANVAS_W * 0.88), CANVAS_H // 2)
NEST_R    = 40
FOOD_R    = 36
MAX_PHERO = 1200   # reduced from 1500 — fewer trail dots = faster rendering

BG_COL    = (8,  12,  20)
NEST_COL  = (100, 60, 220)
FOOD_COL  = (240, 60,  80)
ANT_COL   = (203, 213, 225)
CARRY_COL = (249, 115,  22)
TRAIL_COL = (94, 234, 212)


# ─────────────────────────────────────────
#  DRAW ANT — lightweight, no pre-baked sprites
#  Uses simple ellipses + a direction nub.
#  ~10× faster than rotating 26×26 RGBA images.
# ─────────────────────────────────────────
def draw_ant(draw, x, y, angle, carrying):
    cx, cy = int(x), int(y)
    ca, sa = math.cos(angle), math.sin(angle)
    # body
    draw.ellipse([cx-5, cy-3, cx+5, cy+3], fill=ANT_COL)
    # head (points in direction of travel)
    hx, hy = int(cx + ca * 7), int(cy + sa * 7)
    draw.ellipse([hx-3, hy-3, hx+3, hy+3], fill=ANT_COL)
    # abdomen nub behind
    ax, ay = int(cx - ca * 6), int(cy - sa * 6)
    draw.ellipse([ax-3, ay-2, ax+3, ay+2], fill=ANT_COL)
    # legs (3 lines each side — cheap)
    for i in (-1, 0, 1):
        off = i * 3
        lx0 = int(cx - sa * off)
        ly0 = int(cy + ca * off)
        draw.line([(lx0, ly0), (int(lx0 - sa * 6 - ca * 2), int(ly0 + ca * 6 - sa * 2))],
                  fill=(150, 160, 175), width=1)
        draw.line([(lx0, ly0), (int(lx0 + sa * 6 - ca * 2), int(ly0 - ca * 6 - sa * 2))],
                  fill=(150, 160, 175), width=1)
    # food dot
    if carrying:
        draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=CARRY_COL)


# ─────────────────────────────────────────
#  OBSTACLES
# ─────────────────────────────────────────
def point_in_obstacle(x, y, obstacles):
    for o in obstacles:
        if math.hypot(x-o['x'], y-o['y']) < o['r']:
            return True
    return False

def build_obstacles(preset):
    obs,cx,cy = [], CANVAS_W//2, CANVAS_H//2
    if preset == "Wall":
        for i in range(-5,6):
            obs.append({'x':cx,'y':cy+i*42,'r':20})
    elif preset == "Maze":
        for i in range(-3,4):
            obs.append({'x':cx+i*55,'y':cy-85,'r':22})
        for i in range(-2,5):
            obs.append({'x':cx-30+i*55,'y':cy+85,'r':22})
    elif preset == "Random":
        rng = random.Random(42)
        for _ in range(8):
            obs.append({'x':rng.randint(200,CANVAS_W-200),
                        'y':rng.randint(70,CANVAS_H-70),
                        'r':rng.randint(18,36)})
    return obs


# ─────────────────────────────────────────
#  ANT AGENT
# ─────────────────────────────────────────
class Ant:
    __slots__ = ('x','y','angle','speed','hasFood')
    def __init__(self):
        self.x,self.y   = NEST_POS[0]+random.uniform(-8,8), NEST_POS[1]+random.uniform(-8,8)
        self.angle      = random.uniform(0, math.pi*2)
        self.speed      = 3.5 + random.uniform(0,1.8)
        self.hasFood    = False

    def update(self, pheromones, strength, speed_mult, wander, obstacles):
        nx,ny = NEST_POS; fx,fy = FOOD_POS
        spd   = self.speed * speed_mult
        if not self.hasFood and math.hypot(fx-self.x,fy-self.y) < FOOD_R+4:
            self.hasFood=True; self.angle=math.atan2(ny-self.y,nx-self.x); return True
        if self.hasFood and math.hypot(nx-self.x,ny-self.y) < NEST_R+4:
            self.hasFood=False; self.angle=random.uniform(0,math.pi*2); return False
        if self.hasFood and random.random()<0.18:
            pheromones.append({'x':self.x,'y':self.y,'life':255*strength})
            if len(pheromones)>MAX_PHERO: pheromones.pop(0)
        if self.hasFood:
            t=math.atan2(ny-self.y,nx-self.x); self.angle+=(t-self.angle)*0.18
        else:
            bd,bp=999,None
            for p in pheromones:
                d=math.hypot(p['x']-self.x,p['y']-self.y)
                if d<60 and d<bd: bd,bp=d,p
            if bp:
                t=math.atan2(fy-self.y,fx-self.x); self.angle+=(t-self.angle)*0.35
            else:
                self.angle+=(random.random()-.5)*wander
        nx_=self.x+math.cos(self.angle)*spd; ny_=self.y+math.sin(self.angle)*spd
        if point_in_obstacle(nx_,ny_,obstacles):
            self.angle+=math.pi*0.5+random.uniform(-.4,.4)
            nx_=self.x+math.cos(self.angle)*spd; ny_=self.y+math.sin(self.angle)*spd
        self.x,self.y=nx_,ny_
        if self.x<5 or self.x>CANVAS_W-5:
            self.angle=math.pi-self.angle; self.x=max(5,min(CANVAS_W-5,self.x))
        if self.y<5 or self.y>CANVAS_H-5:
            self.angle=-self.angle; self.y=max(5,min(CANVAS_H-5,self.y))
        return None


# ─────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────
def _init(n=80):
    st.session_state.colony         = [Ant() for _ in range(n)]
    st.session_state.pheromones     = []
    st.session_state.food_collected = 0
    st.session_state.tick           = 0
    st.session_state.rate_buf       = []
    st.session_state.trail_heatmap  = {}
    st.session_state.prev_collected = 0
    st.session_state.best_rate      = 0

if 'colony' not in st.session_state:
    st.session_state.num_ants = 80
    st.session_state.running  = False
    _init()

for k,v in [('rate_buf',[]),('trail_heatmap',{}),('prev_collected',0),
            ('best_rate',0),('running',False),('num_ants',80)]:
    if k not in st.session_state:
        st.session_state[k] = v

def reset_sim():
    st.session_state.running = False
    _init(st.session_state.num_ants)

def start_sim(): st.session_state.running = True
def stop_sim():  st.session_state.running = False


# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#0f1623,#161e2e);padding:15px 17px;'
        'border-radius:14px;border:1px solid rgba(94,234,212,.15);margin-bottom:12px">'
        '<div style="font-size:9px;color:#64748b;text-transform:uppercase;letter-spacing:.12em;'
        'margin-bottom:4px;font-family:DM Mono,monospace">Developer</div>'
        '<div style="font-size:19px;font-weight:800;color:#5eead4;font-family:Syne,sans-serif;'
        'line-height:1.2">EKEH FAVOUR<br>JUNIOR</div>'
        '<div style="margin-top:10px;border-top:1px solid rgba(255,255,255,.06);padding-top:9px;'
        'font-size:11px;color:#94a3b8;font-family:DM Mono,monospace">'
        '<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
        '<span>REG</span><strong style="color:#e2e8f0">20231390832</strong></div>'
        '<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
        '<span>DEPT</span><strong style="color:#e2e8f0">CYBERSECURITY</strong></div>'
        '<div style="display:flex;justify-content:space-between">'
        '<span>COURSE</span><strong style="color:#e2e8f0">CSC309</strong></div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown("### Swarm Controls")
    new_n = st.slider("Colony Size", 10, 200, st.session_state.num_ants, 10)  # cap at 200
    if new_n != st.session_state.num_ants:
        st.session_state.num_ants = new_n
        reset_sim()

    speed_label = st.radio("Simulation Speed",
                           ["Slow","Normal","Fast","Turbo"], index=1, horizontal=True)
    speed_map   = {"Slow":0.5,"Normal":1.0,"Fast":1.8,"Turbo":3.0}
    sim_speed   = speed_map[speed_label]

    wander    = st.slider("Wander Factor", 0.1, 2.0, 0.7, 0.05,
                          help="Higher = more random exploration.")

    st.markdown("### Pheromone Engine")
    strength  = st.slider("Trail Strength",   0.1, 1.0, 0.75, 0.05)
    evap_rate = st.slider("Evaporation Rate", 0.005, 0.25, 0.018, 0.005)

    st.markdown("### Visualisation")
    show_heatmap = st.toggle("Heat-map Overlay",      value=False)
    show_trails  = st.toggle("Show Pheromone Trails",  value=True)
    trail_glow   = st.toggle("Trail Glow Effect",      value=False)

    st.markdown("### Obstacles")
    obs_mode = st.selectbox("Obstacle Preset", ["None","Wall","Maze","Random"])

    st.markdown("---")
    col_r, col_run, col_s = st.columns(3)

    with col_r:
        st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
        st.button("↺ RESET", on_click=reset_sim, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_run:
        if not st.session_state.running:
            st.markdown('<div class="btn-run">', unsafe_allow_html=True)
            st.button("▶ RUN", on_click=start_sim, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="btn-stop">', unsafe_allow_html=True)
            st.button("⏸ STOP", on_click=stop_sim, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_s:
        def step_sim():
            if not st.session_state.running:
                obs = build_obstacles(obs_mode)
                for ant in st.session_state.colony:
                    r = ant.update(st.session_state.pheromones,
                                   strength, sim_speed, wander, obs)
                    if r is False:
                        st.session_state.food_collected += 1
                st.session_state.tick += 1
        st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
        st.button("⏭ STEP", on_click=step_sim, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
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
        '4. Evaporation prunes weak paths &mdash; emergent optimal routing.<br><br>'
        '<strong style="color:#e2e8f0">Extensions:</strong><br>'
        '&bull; Obstacle avoidance &bull; Delivery rate tracking<br>'
        '&bull; Heat-map overlay &bull; Wander factor tuning<br>'
        '&bull; Step-through mode &bull; Speed presets'
        '</div></details>',
        unsafe_allow_html=True
    )

current_obstacles = build_obstacles(obs_mode)
run_simulation    = st.session_state.running


# ─────────────────────────────────────────
#  PHYSICS TICK
#  Reduced to 3 steps per frame (was 8).
#  Fewer steps = lighter CPU load per rerun,
#  so the canvas actually refreshes visibly.
# ─────────────────────────────────────────
STEPS_PER_FRAME = 3   # ← was 8; keep low for cloud

if run_simulation:
    now = time.time()
    for _ in range(STEPS_PER_FRAME):
        st.session_state.tick += 1
        # evaporation
        alive = []
        for p in st.session_state.pheromones:
            p['life'] -= evap_rate * 60
            if p['life'] > 0: alive.append(p)
        st.session_state.pheromones = alive
        # agent updates
        for ant in st.session_state.colony:
            result = ant.update(st.session_state.pheromones,
                                strength, sim_speed, wander, current_obstacles)
            if result is False:
                st.session_state.food_collected += 1
                st.session_state.rate_buf.append(now)
            if show_heatmap:
                cell=(int(ant.x)//8, int(ant.y)//8)
                st.session_state.trail_heatmap[cell] = \
                    st.session_state.trail_heatmap.get(cell,0) + 1


# ─────────────────────────────────────────
#  DRAW FRAME
#  Ants are now drawn with draw_ant() —
#  no PIL image-paste / alpha compositing.
# ─────────────────────────────────────────
def draw_frame():
    img  = Image.new("RGB", (CANVAS_W,CANVAS_H), BG_COL)
    draw = ImageDraw.Draw(img)

    # grid
    for gx in range(0,CANVAS_W,60):
        draw.line([(gx,0),(gx,CANVAS_H)], fill=(18,24,36), width=1)
    for gy in range(0,CANVAS_H,60):
        draw.line([(0,gy),(CANVAS_W,gy)], fill=(18,24,36), width=1)

    # heatmap
    if show_heatmap and st.session_state.trail_heatmap:
        hm=st.session_state.trail_heatmap; mx=max(hm.values()) or 1
        for (gx,gy),val in hm.items():
            t=min(val/mx,1.0)
            draw.rectangle([gx*8,gy*8,gx*8+8,gy*8+8],
                           fill=(int(20+t*120),int(t*50),int(t*80)))

    # pheromone trails
    if show_trails:
        if trail_glow:
            tl=Image.new("RGB",(CANVAS_W,CANVAS_H),BG_COL); td=ImageDraw.Draw(tl)
            for p in st.session_state.pheromones:
                t=max(0,min(1,p['life']/255))
                td.rectangle([p['x']-1,p['y']-1,p['x']+2,p['y']+2],
                             fill=(int(TRAIL_COL[0]*t),int(TRAIL_COL[1]*t),int(TRAIL_COL[2]*t)))
            blended=Image.blend(img,tl.filter(ImageFilter.GaussianBlur(2)),alpha=0.7)
            img=blended; draw=ImageDraw.Draw(img)
        else:
            for p in st.session_state.pheromones:
                t=max(0,min(1,p['life']/255))
                draw.rectangle([p['x']-1,p['y']-1,p['x']+2,p['y']+2],
                               fill=(int(TRAIL_COL[0]*t),int(TRAIL_COL[1]*t),int(TRAIL_COL[2]*t)))

    # obstacles
    for o in current_obstacles:
        draw.ellipse([o['x']-o['r'],o['y']-o['r'],o['x']+o['r'],o['y']+o['r']],
                     fill=(28,35,52), outline=(60,80,110), width=2)

    # nest rings + fill
    for rh in (58,46,34):
        draw.ellipse([NEST_POS[0]-rh,NEST_POS[1]-rh,NEST_POS[0]+rh,NEST_POS[1]+rh],
                     outline=NEST_COL, width=1)
    draw.ellipse([NEST_POS[0]-NEST_R,NEST_POS[1]-NEST_R,
                  NEST_POS[0]+NEST_R,NEST_POS[1]+NEST_R], fill=NEST_COL)
    draw.text((NEST_POS[0]-7,NEST_POS[1]-7), "N", fill=(200,190,255))

    # food rings + fill
    for rh in (52,40,28):
        draw.ellipse([FOOD_POS[0]-rh,FOOD_POS[1]-rh,FOOD_POS[0]+rh,FOOD_POS[1]+rh],
                     outline=FOOD_COL, width=1)
    draw.ellipse([FOOD_POS[0]-FOOD_R,FOOD_POS[1]-FOOD_R,
                  FOOD_POS[0]+FOOD_R,FOOD_POS[1]+FOOD_R], fill=FOOD_COL)
    draw.text((FOOD_POS[0]-5,FOOD_POS[1]-7), "F", fill=(255,220,200))

    # ants — lightweight vector drawing, no sprite paste
    for ant in st.session_state.colony:
        if 5 < ant.x < CANVAS_W-5 and 5 < ant.y < CANVAS_H-5:
            draw_ant(draw, ant.x, ant.y, ant.angle, ant.hasFood)

    # legend
    lx,ly = CANVAS_W-160, CANVAS_H-70
    draw.rectangle([lx-8,ly-8,CANVAS_W-6,CANVAS_H-6], fill=(12,18,30), outline=(40,55,80))
    draw.ellipse([lx,ly+2,lx+12,ly+14],  fill=NEST_COL)
    draw.text(  (lx+16,ly+2),  "Nest",  fill=(180,170,240))
    draw.ellipse([lx,ly+20,lx+12,ly+32], fill=FOOD_COL)
    draw.text(  (lx+16,ly+20), "Food",  fill=(255,200,190))
    draw.rectangle([lx,ly+38,lx+12,ly+44], fill=TRAIL_COL)
    draw.text(  (lx+16,ly+38), "Trail", fill=(160,240,220))

    # status dot
    status_col = (34,197,94) if run_simulation else (100,116,139)
    draw.ellipse([8,8,18,18], fill=status_col)

    return img


# ─────────────────────────────────────────
#  STATS
# ─────────────────────────────────────────
def compute_rate():
    now=time.time()
    st.session_state.rate_buf=[t for t in st.session_state.rate_buf if now-t<60]
    return len(st.session_state.rate_buf)

def render_stats(food, colony_sz, carrying, rate, best_rate, trails, ticks, eff):
    delta  = food - st.session_state.prev_collected
    d_html = (f'<span style="color:#22c55e;font-size:.7rem"> +{delta}</span>' if delta else "")
    rs     = f'<span style="font-size:.65rem;color:#64748b"> best {best_rate}</span>'
    os_    = f'<span style="font-size:.65rem;color:#64748b"> / {colony_sz}</span>'
    eff_c  = min(100,eff)
    spd_col= {"Slow":"#64748b","Normal":"#5eead4","Fast":"#f59e0b","Turbo":"#f43f5e"}
    sc     = spd_col.get(speed_label,"#5eead4")
    run_state="RUNNING" if run_simulation else "PAUSED"
    run_col  ="#22c55e"  if run_simulation else "#64748b"

    def card(lbl,val,sub=""):
        return (
            '<div style="background:#161e2e;border:1px solid rgba(94,234,212,.15);'
            f'border-radius:14px;padding:11px 15px">'
            f'<div style="font-size:.6rem;color:#64748b;text-transform:uppercase;'
            f'letter-spacing:.07em;font-family:DM Mono,monospace;margin-bottom:4px">{lbl}</div>'
            f'<div style="font-size:1.3rem;color:#5eead4;font-family:DM Mono,monospace;'
            f'line-height:1.1">{val}{sub}</div></div>'
        )

    return (
        '<div class="stat-panel">'
        + f'<div style="background:#161e2e;border:1px solid rgba(94,234,212,.15);border-radius:14px;'
          f'padding:10px 15px;display:flex;justify-content:space-between;align-items:center">'
          f'<span style="font-size:.6rem;color:#64748b;text-transform:uppercase;'
          f'letter-spacing:.07em;font-family:DM Mono,monospace">Status</span>'
          f'<span style="font-size:.75rem;font-family:DM Mono,monospace;color:{run_col};'
          f'font-weight:600">{run_state}</span></div>'
        + f'<div style="background:#161e2e;border:1px solid rgba(94,234,212,.15);border-radius:14px;'
          f'padding:10px 15px;display:flex;justify-content:space-between;align-items:center">'
          f'<span style="font-size:.6rem;color:#64748b;text-transform:uppercase;'
          f'letter-spacing:.07em;font-family:DM Mono,monospace">Speed</span>'
          f'<span style="font-size:.75rem;font-family:DM Mono,monospace;color:{sc}">{speed_label}</span></div>'
        + card("Biomass Harvested", food, d_html)
        + card("Payload Carriers",  carrying, os_)
        + card("Rate  units/min",   rate, rs)
        + card("Active Trails",     trails)
        + card("Sim Ticks",         ticks)
        + '<div style="background:#161e2e;border:1px solid rgba(94,234,212,.15);'
          'border-radius:14px;padding:11px 15px">'
          '<div style="font-size:.6rem;color:#64748b;text-transform:uppercase;'
          'letter-spacing:.07em;font-family:DM Mono,monospace;margin-bottom:6px">'
          f'Carrier Efficiency <span style="color:#5eead4">{eff_c}%</span></div>'
          '<div class="eff-bar-wrap">'
          f'<div class="eff-bar-fill" style="width:{eff_c}%"></div>'
          '</div></div>'
        '</div>'
    )


# ─────────────────────────────────────────
#  MAIN LAYOUT
# ─────────────────────────────────────────
badge = ('<span class="badge badge-run">&#9679; RUNNING</span>'
         if run_simulation else
         '<span class="badge badge-idle">&#9675; IDLE</span>')

st.markdown(
    f'<div style="margin-bottom:5px">'
    f'<span style="font-family:Syne,sans-serif;font-size:1.65rem;font-weight:800;color:#5eead4">'
    f'Ant Colony Optimisation</span>&nbsp;&nbsp;{badge}</div>'
    f'<div style="font-size:.75rem;color:#64748b;font-family:DM Mono,monospace;'
    f'letter-spacing:.04em;margin-bottom:10px">Swarm intelligence foraging simulator '
    f'&middot; CSC309 &middot; Speed: <span style="color:#5eead4">{speed_label}</span></div>',
    unsafe_allow_html=True
)

canvas_col, stats_col = st.columns([5,2])
with canvas_col:
    st.image(draw_frame(), use_container_width=True, output_format="JPEG")

carrying = sum(1 for a in st.session_state.colony if a.hasFood)
rate     = compute_rate()
if rate > st.session_state.best_rate:
    st.session_state.best_rate = rate
eff = min(100, int(carrying / max(1,len(st.session_state.colony)) * 100))

with stats_col:
    st.markdown(
        render_stats(st.session_state.food_collected, len(st.session_state.colony),
                     carrying, rate, st.session_state.best_rate,
                     len(st.session_state.pheromones), st.session_state.tick, eff),
        unsafe_allow_html=True
    )

st.session_state.prev_collected = st.session_state.food_collected

# ── Drive animation ──
# NO time.sleep() before rerun — on Streamlit Cloud the
# rerun round-trip itself provides the frame-rate throttle.
if run_simulation:
    st.rerun()

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from urllib.parse import quote
import os, zipfile

st.set_page_config(page_title="Business Stage Map", page_icon="📍", layout="centered")

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {max-width: 940px; padding-top: 2rem; padding-bottom: 3rem;}
    h1, h2, h3 {letter-spacing: -0.02em;}
    .eyebrow {font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color:#6B7280;}
    .hero-title {font-size: 2.15rem; font-weight: 800; line-height:1.08; margin: 0.2rem 0 0.5rem 0;}
    .meta {font-size: 1.02rem; color:#374151; margin-bottom: 0.25rem;}
    .pill {display:inline-block; padding:0.35rem 0.7rem; border-radius:999px; background:#F3F4F6; margin-right:0.4rem; margin-bottom:0.4rem; font-weight:600; font-size:0.9rem;}
    .result-card {padding:0.95rem 1.05rem; border-radius:16px; border:1px solid #E5E7EB; background:#FFFFFF; margin-top:0.8rem; box-shadow:0 6px 20px rgba(17,24,39,0.04);}
    .result-label {font-size:0.76rem; text-transform:uppercase; letter-spacing:0.08em; color:#6B7280; font-weight:700;}
    .result-value {font-size:1.18rem; font-weight:800; color:#111827; margin-top:0.15rem;}
    .next-move {padding:1rem 1.1rem; border-left:3px solid #111827; background:#F9FAFB; border-radius:10px; margin-top:1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Query params
# -----------------------------
qp = st.query_params

def q(name, default):
    val = qp.get(name, default)
    if isinstance(val, list):
        return val[0]
    return val

business_type = str(q("type", "Product")).title()
stage = str(q("stage", "Growing")).title()
concern = str(q("concern", "Getting customers")).replace("+", " ")

try:
    x_score = float(q("x", 7.2))
except Exception:
    x_score = 7.2
try:
    y_score = float(q("y", 4.5))
except Exception:
    y_score = 4.5

if x_score > 10:
    x_score = x_score / 10
if y_score > 10:
    y_score = y_score / 10
x_score = max(0, min(10, x_score))
y_score = max(0, min(10, y_score))

# -----------------------------
# Benchmarks
# -----------------------------
benchmarks = {
    ("Product", "Starting"): ((2.0, 4.5), (1.5, 4.5)),
    ("Product", "Growing"): ((5.0, 7.5), (4.5, 7.0)),
    ("Product", "Established"): ((7.0, 10.0), (6.5, 10.0)),
    ("Service", "Starting"): ((2.0, 4.5), (1.5, 4.5)),
    ("Service", "Growing"): ((4.5, 6.5), (4.0, 6.5)),
    ("Service", "Established"): ((6.5, 9.0), (6.5, 10.0)),
    ("Content", "Starting"): ((2.0, 4.5), (1.5, 4.5)),
    ("Content", "Growing"): ((5.0, 7.5), (4.0, 6.5)),
    ("Content", "Established"): ((7.5, 10.0), (6.5, 10.0)),
    ("Local", "Starting"): ((2.5, 5.0), (2.0, 5.0)),
    ("Local", "Growing"): ((5.5, 7.5), (5.0, 7.5)),
    ("Local", "Established"): ((7.0, 10.0), (7.0, 10.0)),
    ("Hybrid", "Starting"): ((2.5, 5.0), (2.0, 5.0)),
    ("Hybrid", "Growing"): ((5.5, 8.0), (5.0, 7.5)),
    ("Hybrid", "Established"): ((7.0, 10.0), (7.0, 10.0)),
}

benchmark_stage = "Growing" if stage == "Fixing" else stage
x_range, y_range = benchmarks.get((business_type, benchmark_stage), ((4.5, 7.5), (4.5, 7.5)))

# -----------------------------
# Labels and diagnostics
# -----------------------------
def level(score, axis):
    if score < 3.5:
        return "Early"
    if score < 5.5:
        return "Developing"
    if score < 7.5:
        return "Strong"
    return "Broad" if axis == "x" else "Mature"

x_label = level(x_score, "x")
y_label = level(y_score, "y")

cut = 5.5
if x_score < cut and y_score < cut:
    quadrant = "Building the Base"
elif x_score >= cut and y_score < cut:
    quadrant = "Growing Pains"
elif x_score < cut and y_score >= cut:
    quadrant = "Ready for More Customers"
else:
    quadrant = "In Balance"

def distance_from_range(v, rng):
    lo, hi = rng
    if lo <= v <= hi:
        return 0
    return lo - v if v < lo else v - hi

dx = distance_from_range(x_score, x_range)
dy = distance_from_range(y_score, y_range)
max_d = max(dx, dy)

if stage == "Fixing":
    stage_fit = "Fixing mode"
elif dx == 0 and dy == 0:
    stage_fit = "On track"
elif max_d <= 1.0:
    stage_fit = "A little uneven"
elif max_d <= 2.0:
    stage_fit = "Out of balance"
else:
    stage_fit = "Needs attention"

if quadrant == "Growing Pains":
    interpretation = (
        f"Your market reach is ahead of your operating maturity. For a {stage.lower()} {business_type.lower()} business, "
        "this usually means demand is developing faster than the systems supporting it."
    )
    next_move = "Do not add another marketing channel yet. Strengthen delivery, capacity and repeatability first."
elif quadrant == "Ready for More Customers":
    interpretation = (
        "Your operating maturity is stronger than your market reach. You appear capable of handling more demand than you are currently generating."
    )
    next_move = "Use the capacity you already have. Strengthen one additional acquisition channel before adding more operational complexity."
elif quadrant == "Building the Base":
    interpretation = (
        "Your reach and operating maturity are both still concentrated. That can be appropriate early on, but it becomes a constraint if the business is already beyond the proving stage."
    )
    next_move = "Focus on proving one dependable route to customers and one repeatable delivery process before broadening the model."
else:
    interpretation = (
        "Your market reach and operating maturity are developing together. The business has a healthier balance between generating demand and delivering it consistently."
    )
    next_move = "Protect what is working. Improve resilience, margins and channel quality before adding unnecessary complexity."

if stage == "Fixing":
    interpretation += " You also identified the business as being in Fixing mode, so stabilization should take priority over expansion."
    next_move = "Return to the channels, offers and processes that produce cash and reliability fastest. Stabilize first; expand second."

concern_lower = concern.lower()
if "customer" in concern_lower or "lead" in concern_lower:
    if x_score >= 5.5 and y_score < 5.5:
        perceived_note = "You said getting customers is the biggest concern, but the map suggests operational capacity may be the more immediate constraint."
    else:
        perceived_note = "Your stated concern about customer acquisition is broadly consistent with the market-reach signal in the map."
elif "smarter" in concern_lower or "efficien" in concern_lower:
    perceived_note = "Your concern about working smarter is most closely related to the operational-maturity side of the map."
elif "money" in concern_lower or "cash" in concern_lower or "profit" in concern_lower:
    perceived_note = "Your money concern should be read alongside both reach and maturity: weak demand and inefficient delivery can each create cash pressure for different reasons."
elif "keeping" in concern_lower or "loyal" in concern_lower:
    perceived_note = "Your concern about retention is not fully captured by the X/Y map, so treat it as an additional diagnostic flag rather than part of the plotted score."
else:
    perceived_note = "Your stated concern adds context to the map, but it is not included directly in the X/Y score."

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="eyebrow">Business diagnostic</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Your Business Stage Map</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="meta"><b>Self-identified stage:</b> {stage} &nbsp;&nbsp; <b>Your position:</b> {quadrant}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<span class="pill">{business_type}</span><span class="pill">Concern: {concern}</span>',
    unsafe_allow_html=True,
)

# -----------------------------
# Integrated bell + quadrant chart
# -----------------------------
fig = go.Figure()

# Curve
x = np.linspace(0, 10, 600)
curve = 7.8 * np.exp(-((x - 5.7) ** 2) / 9.2)
curve = np.clip(curve, 0.35, 8.0)

# Subtle stage fills under curve
segments = [
    (0, 3.4, "rgba(229, 213, 206, 0.55)"),
    (3.4, 6.8, "rgba(215, 229, 215, 0.62)"),
    (6.8, 10, "rgba(214, 222, 235, 0.65)")
]
for a, b, color in segments:
    mask = (x >= a) & (x <= b)
    fig.add_trace(go.Scatter(
        x=x[mask], y=curve[mask], mode="lines", line=dict(width=0),
        fill="tozeroy", fillcolor=color, hoverinfo="skip", showlegend=False
    ))

# Bell curve (thin + dashed)
fig.add_trace(go.Scatter(
    x=x, y=curve, mode="lines",
    line=dict(color="rgba(100,116,139,0.75)", width=1.8, dash="dash"),
    hoverinfo="skip", showlegend=False
))

# Thin quadrant lines
axis_color = "rgba(71,85,105,0.55)"
fig.add_shape(type="line", x0=cut, x1=cut, y0=0, y1=10,
              line=dict(color=axis_color, width=1.2))
fig.add_shape(type="line", x0=0, x1=10, y0=cut, y1=cut,
              line=dict(color=axis_color, width=1.2))

# Stage separators along x only in lower band
for xsep in [3.4, 6.8]:
    fig.add_shape(type="line", x0=xsep, x1=xsep, y0=0, y1=0.6,
                  line=dict(color="rgba(100,116,139,0.45)", width=1, dash="dot"))

# Expected zone rectangle - softer distinct color
fig.add_shape(
    type="rect", x0=x_range[0], x1=x_range[1], y0=y_range[0], y1=y_range[1],
    fillcolor="rgba(16, 185, 129, 0.14)", line=dict(color="rgba(16, 185, 129, 0.6)", width=1.1, dash="dot")
)

# "You should be here" annotation
fig.add_annotation(
    x=(x_range[0] + x_range[1]) / 2,
    y=min(9.5, y_range[1] + 0.45),
    text="You should be here",
    showarrow=False,
    font=dict(size=11, color="#047857"),
    bgcolor="rgba(236,253,245,0.9)",
    bordercolor="rgba(16,185,129,0.18)",
    borderpad=4,
)

# Cross marker + label
fig.add_trace(go.Scatter(
    x=[x_score], y=[y_score], mode="markers+text",
    marker=dict(symbol="x", size=18, color="#111827", line=dict(width=2, color="#111827")),
    text=["You're here"], textposition="top center", textfont=dict(size=11, color="#111827"),
    hovertemplate=f"Market Reach: {x_score:.1f}<br>Operational Maturity: {y_score:.1f}<extra></extra>",
    showlegend=False
))

# Quadrant labels - small and plain
qfont = dict(size=11, color="rgba(71,85,105,0.72)")
fig.add_annotation(x=1.9, y=8.4, text="Ready for more<br>customers", showarrow=False, font=qfont, align="center")
fig.add_annotation(x=8.1, y=8.4, text="In balance", showarrow=False, font=qfont, align="center")
fig.add_annotation(x=1.8, y=0.95, text="Building the base", showarrow=False, font=qfont, align="center")
fig.add_annotation(x=8.15, y=0.95, text="Growing pains", showarrow=False, font=qfont, align="center")

# Stage labels outside chart (below)
stage_font = dict(size=12, color="#6B7280")
fig.add_annotation(x=1.7, y=-0.08, xref="x", yref="paper", text="Starting", showarrow=False, font=stage_font)
fig.add_annotation(x=5.1, y=-0.08, xref="x", yref="paper", text="Growing", showarrow=False, font=stage_font)
fig.add_annotation(x=8.3, y=-0.08, xref="x", yref="paper", text="Established", showarrow=False, font=stage_font)

# Axis labels as annotations for cleaner style
fig.add_annotation(
    x=5, y=-0.18, xref="x", yref="paper",
    text="<b>Market reach</b> → more ways people can find and buy from you",
    showarrow=False, font=dict(size=12, color="#6B7280")
)
fig.add_annotation(
    x=-0.08, y=5, xref="paper", yref="y",
    text="<b>Operational maturity</b> → more repeatable systems in the business",
    showarrow=False, textangle=-90, font=dict(size=12, color="#6B7280")
)

fig.update_layout(
    height=340,
    margin=dict(l=42, r=18, t=10, b=72),
    paper_bgcolor="white",
    plot_bgcolor="#FCFCFB",
    xaxis=dict(range=[0, 10], showgrid=False, zeroline=False, showticklabels=False, title=""),
    yaxis=dict(range=[0, 10], showgrid=False, zeroline=False, showticklabels=False, title=""),
    hoverlabel=dict(bgcolor="white", font_size=12),
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

# -----------------------------
# Results
# -----------------------------
c1, c2 = st.columns(2)
with c1:
    st.markdown(f'<div class="result-card"><div class="result-label">Market Reach</div><div class="result-value">{x_label}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="result-card"><div class="result-label">Operational Maturity</div><div class="result-value">{y_label}</div></div>', unsafe_allow_html=True)

st.markdown(f"### Your stage fit: **{stage_fit}**")
st.write(interpretation)
st.caption(perceived_note)
st.markdown(f'<div class="next-move"><b>Next move:</b> {next_move}</div>', unsafe_allow_html=True)

with st.expander("What this map is measuring"):
    st.write(
        "Market Reach reflects the breadth and diversity of how customers find and buy from you. "
        "Operational Maturity reflects the repeatability of the systems that support delivery. "
        "Your stage fit compares those observed signals with the benchmark range for your business type and self-identified stage."
    )

st.divider()
st.caption("Prototype testing controls")
with st.expander("Try another result"):
    demo_type = st.selectbox("Business type", ["Product", "Service", "Content", "Local", "Hybrid"], index=["Product", "Service", "Content", "Local", "Hybrid"].index(business_type) if business_type in ["Product", "Service", "Content", "Local", "Hybrid"] else 0)
    demo_stage = st.selectbox("Stage", ["Starting", "Growing", "Established", "Fixing"], index=["Starting", "Growing", "Established", "Fixing"].index(stage) if stage in ["Starting", "Growing", "Established", "Fixing"] else 1)
    demo_concern = st.selectbox("Concern", ["Money", "Getting customers", "Keeping customers", "Working smarter"], index=0)
    demo_x = st.slider("Market Reach", 0.0, 10.0, float(x_score), 0.1)
    demo_y = st.slider("Operational Maturity", 0.0, 10.0, float(y_score), 0.1)
    url = f"?type={quote(demo_type)}&stage={quote(demo_stage)}&concern={quote(demo_concern)}&x={demo_x}&y={demo_y}"
    st.code(url)
    st.markdown(f"[Open this result]({url})")

# Write a zip copy for the user if running in notebook env
base_dir = '/mnt/data/business_stage_map_streamlit_v3'
os.makedirs(base_dir, exist_ok=True)
for fname in ['app.py', 'requirements.txt', 'README.md']:
    src = os.path.join('/mnt/data/business_stage_map_streamlit', fname)
    if os.path.exists(src):
        with open(src, 'rb') as fsrc, open(os.path.join(base_dir, fname), 'wb') as fdst:
            fdst.write(fsrc.read())
zip_path = '/mnt/data/business_stage_map_streamlit_v3.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for fname in ['app.py', 'requirements.txt', 'README.md']:
        p = os.path.join(base_dir, fname)
        if os.path.exists(p):
            z.write(p, arcname=f'business_stage_map_streamlit_v3/{fname}')

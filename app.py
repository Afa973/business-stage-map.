import streamlit as st
import plotly.graph_objects as go
import numpy as np
from urllib.parse import quote

st.set_page_config(page_title="Business Stage Map", page_icon="📍", layout="centered")

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {max-width: 980px; padding-top: 2.2rem; padding-bottom: 4rem;}
    h1, h2, h3 {letter-spacing: -0.02em;}
    .eyebrow {font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color:#6B7280;}
    .hero-title {font-size: 2.15rem; font-weight: 800; line-height:1.08; margin: 0.2rem 0 0.5rem 0;}
    .meta {font-size: 1.02rem; color:#374151; margin-bottom: 0.25rem;}
    .pill {display:inline-block; padding:0.35rem 0.7rem; border-radius:999px; background:#F3F4F6; margin-right:0.4rem; margin-bottom:0.4rem; font-weight:600; font-size:0.9rem;}
    .result-card {padding:1.1rem 1.2rem; border-radius:18px; border:1px solid #E5E7EB; background:#FFFFFF; margin-top:0.8rem; box-shadow:0 8px 28px rgba(17,24,39,0.05);}
    .result-label {font-size:0.76rem; text-transform:uppercase; letter-spacing:0.08em; color:#6B7280; font-weight:700;}
    .result-value {font-size:1.18rem; font-weight:800; color:#111827; margin-top:0.15rem;}
    .next-move {padding:1rem 1.1rem; border-left:4px solid #111827; background:#F9FAFB; border-radius:10px; margin-top:1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Query params (works with Tally redirects later)
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

# Expect simple 0–10 scale. Keep robust to 0–100 incoming values.
if x_score > 10:
    x_score = x_score / 10
if y_score > 10:
    y_score = y_score / 10
x_score = max(0, min(10, x_score))
y_score = max(0, min(10, y_score))

# -----------------------------
# Benchmarks (simple first version; can be tuned from workbook)
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

# If fixing is selected, use growing as a neutral comparison while flagging fixing separately.
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

# Interpretation
if quadrant == "Growing Pains":
    interpretation = (
        f"Your market reach is ahead of your operating maturity. For a {stage.lower()} {business_type.lower()} business, "
        "this usually means demand is developing faster than the systems supporting it."
    )
    next_move = "Do not add another marketing channel yet. Strengthen delivery, capacity and repeatability first."
elif quadrant == "Ready for More Customers":
    interpretation = (
        f"Your operating maturity is stronger than your market reach. You appear capable of handling more demand than you are currently generating."
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

# Add perceived-vs-observed insight
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

# Background stage zones, clipped approximately by bell shape using translucent fills.
x = np.linspace(0, 10, 500)
# smooth lifecycle curve: rise, peak, decline
curve = 7.8 * np.exp(-((x - 5.7) ** 2) / 9.5)
curve = np.clip(curve, 0.3, 8.0)

# Stage fills under curve
stage_segments = [
    (0, 3.4, "rgba(244, 207, 201, 0.30)"),
    (3.4, 6.8, "rgba(206, 231, 209, 0.34)"),
    (6.8, 10, "rgba(202, 219, 241, 0.34)"),
]
for a, b, color in stage_segments:
    mask = (x >= a) & (x <= b)
    fig.add_trace(go.Scatter(
        x=x[mask], y=curve[mask], mode="lines", line=dict(width=0),
        fill="tozeroy", fillcolor=color, hoverinfo="skip", showlegend=False
    ))

# Curve line
fig.add_trace(go.Scatter(
    x=x, y=curve, mode="lines", line=dict(color="rgba(55,65,81,0.55)", width=3),
    hoverinfo="skip", showlegend=False
))

# Quadrant lines OVER the curve
fig.add_shape(type="line", x0=cut, x1=cut, y0=0, y1=10,
              line=dict(color="rgba(31,41,55,0.48)", width=2))
fig.add_shape(type="line", x0=0, x1=10, y0=cut, y1=cut,
              line=dict(color="rgba(31,41,55,0.48)", width=2))

# Expected benchmark zone
fig.add_shape(
    type="rect", x0=x_range[0], x1=x_range[1], y0=y_range[0], y1=y_range[1],
    fillcolor="rgba(17,24,39,0.04)", line=dict(color="rgba(17,24,39,0.32)", width=1.5, dash="dot")
)

# Reader point + halo
fig.add_trace(go.Scatter(
    x=[x_score], y=[y_score], mode="markers+text",
    marker=dict(size=32, color="rgba(17,24,39,0.10)", line=dict(width=0)),
    hoverinfo="skip", showlegend=False
))
fig.add_trace(go.Scatter(
    x=[x_score], y=[y_score], mode="markers",
    marker=dict(size=14, color="#111827", line=dict(color="white", width=3)),
    hovertemplate=f"Market Reach: {x_score:.1f}<br>Operational Maturity: {y_score:.1f}<extra></extra>",
    showlegend=False
))

# Stage labels
fig.add_annotation(x=1.5, y=1.7, text="STARTING", showarrow=False, font=dict(size=12, color="#7C6F6B"))
fig.add_annotation(x=5.0, y=6.6, text="GROWING", showarrow=False, font=dict(size=12, color="#607765"))
fig.add_annotation(x=8.2, y=5.6, text="ESTABLISHED", showarrow=False, font=dict(size=12, color="#64748B"))

# Quadrant labels
qfont = dict(size=11, color="rgba(31,41,55,0.62)")
fig.add_annotation(x=2.0, y=8.5, text="READY FOR MORE<br>CUSTOMERS", showarrow=False, font=qfont, align="center")
fig.add_annotation(x=8.0, y=8.5, text="IN BALANCE", showarrow=False, font=qfont, align="center")
fig.add_annotation(x=2.0, y=0.9, text="BUILDING<br>THE BASE", showarrow=False, font=qfont, align="center")
fig.add_annotation(x=8.0, y=0.9, text="GROWING<br>PAINS", showarrow=False, font=qfont, align="center")

# Benchmark annotation
fig.add_annotation(
    x=x_range[1], y=y_range[1], text=f"{business_type} / {benchmark_stage}<br>expected zone",
    showarrow=True, arrowhead=2, ax=45, ay=-35,
    bgcolor="rgba(255,255,255,0.88)", bordercolor="rgba(17,24,39,0.14)", borderpad=5,
    font=dict(size=10, color="#4B5563")
)

fig.update_layout(
    height=430,
    margin=dict(l=28, r=20, t=16, b=48),
    paper_bgcolor="white",
    plot_bgcolor="#FCFCFB",
    xaxis=dict(
        range=[0,10], title="MARKET REACH  →  more ways to find and buy from you", showgrid=False, zeroline=False,
        showticklabels=False, title_font=dict(size=13, color="#6B7280")
    ),
    yaxis=dict(
        range=[0,10], title="OPERATIONAL MATURITY  →  more repeatable systems", showgrid=False, zeroline=False,
        showticklabels=False, title_font=dict(size=13, color="#6B7280")
    ),
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

# Demo controls hidden at bottom for testing before Tally connection
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

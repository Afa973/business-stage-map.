import streamlit as st
import plotly.graph_objects as go
from urllib.parse import quote

st.set_page_config(page_title="Business Stage Map", page_icon="📍", layout="centered")

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {max-width: 940px; padding-top: 2.4rem; padding-bottom: 3rem;}
    h1, h2, h3 {letter-spacing: -0.02em;}
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


# Tally may send the full visible option text, for example:
# "Service — your time or skill" or "Growing — scaling up".
# The app only needs the short category before the descriptive dash.
def short_answer(value):
    text = str(value).replace("+", " ").strip()
    for separator in (" — ", " – ", " - "):
        if separator in text:
            text = text.split(separator, 1)[0].strip()
            break
    return text


business_type = short_answer(q("type", "Product")).title()
stage = short_answer(q("stage", "Growing")).title()
concern = short_answer(q("concern", "Getting customers"))

try:
    x_score = float(q("x", 7.2))
except Exception:
    x_score = 7.2

try:
    y_score = float(q("y", 4.5))
except Exception:
    y_score = 4.5

# Defensive handling in case a score is ever passed on a 0–100 scale.
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

# Fixing is treated as a stabilization state, so the neutral comparison
# remains the Growing benchmark rather than inventing a universal Fixing target.
benchmark_stage = "Growing" if stage == "Fixing" else stage
x_range, y_range = benchmarks.get(
    (business_type, benchmark_stage), ((4.5, 7.5), (4.5, 7.5))
)

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

cut = 5.0

# The lifecycle stage is now read directly from the same X/Y matrix.
if x_score < cut and y_score < cut:
    map_stage = "Starting"
    map_descriptor = "Building the base"
elif x_score < cut and y_score >= cut:
    map_stage = "Growing"
    map_descriptor = "Ready for more customers"
elif x_score >= cut and y_score >= cut:
    map_stage = "Established"
    map_descriptor = "In balance"
else:
    map_stage = "Fixing"
    map_descriptor = "Growing pains"


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

# Core interpretation follows the observed map position.
if map_stage == "Fixing":
    interpretation = (
        f"Your market reach is ahead of your operating maturity. For a {stage.lower()} "
        f"{business_type.lower()} business, this usually means demand is developing faster "
        "than the systems supporting it."
    )
    next_move = (
        "Do not add another marketing channel yet. Strengthen delivery, capacity and "
        "repeatability first."
    )
elif map_stage == "Growing":
    interpretation = (
        "Your operating maturity is stronger than your market reach. You appear capable of "
        "handling more demand than you are currently generating."
    )
    next_move = (
        "Use the capacity you already have. Strengthen one additional acquisition channel "
        "before adding more operational complexity."
    )
elif map_stage == "Starting":
    interpretation = (
        "Your reach and operating maturity are both still concentrated. That can be appropriate "
        "early on, but it becomes a constraint if the business is already beyond the proving stage."
    )
    next_move = (
        "Focus on proving one dependable route to customers and one repeatable delivery process "
        "before broadening the model."
    )
else:
    interpretation = (
        "Your market reach and operating maturity are both relatively strong. The business has "
        "a healthier balance between generating demand and delivering it consistently."
    )
    next_move = (
        "Protect what is working. Improve resilience, margins and channel quality before adding "
        "unnecessary complexity."
    )

# Explicitly compare the user's self-identified stage with the observed map position.
if stage == map_stage:
    stage_comparison = (
        f"Your map position matches the stage you selected: {stage}."
    )
else:
    stage_comparison = (
        f"You identified the business as {stage}, while the current reach/maturity pattern places "
        f"it in the {map_stage} region. That gap is a useful signal to investigate rather than a verdict."
    )

if stage == "Fixing":
    interpretation += (
        " You also identified the business as being in Fixing mode, so stabilization should take "
        "priority over expansion."
    )
    next_move = (
        "Return to the channels, offers and processes that produce cash and reliability fastest. "
        "Stabilize first; expand second."
    )

concern_lower = concern.lower()
if "customer" in concern_lower or "lead" in concern_lower:
    if x_score >= 5.5 and y_score < 5.5:
        perceived_note = (
            "You said getting customers is the biggest concern, but the map suggests operational "
            "capacity may be the more immediate constraint."
        )
    else:
        perceived_note = (
            "Your stated concern about customer acquisition is broadly consistent with the "
            "market-reach signal in the map."
        )
elif "smarter" in concern_lower or "efficien" in concern_lower:
    perceived_note = (
        "Your concern about working smarter is most closely related to the operational-maturity "
        "side of the map."
    )
elif "money" in concern_lower or "cash" in concern_lower or "profit" in concern_lower:
    perceived_note = (
        "Your money concern should be read alongside both reach and maturity: weak demand and "
        "inefficient delivery can each create cash pressure for different reasons."
    )
elif "keeping" in concern_lower or "loyal" in concern_lower:
    perceived_note = (
        "Your concern about retention is not fully captured by the X/Y map, so treat it as an "
        "additional diagnostic flag rather than part of the plotted score."
    )
else:
    perceived_note = (
        "Your stated concern adds context to the map, but it is not included directly in the X/Y score."
    )

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="hero-title">Your Business Stage Map</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="meta"><b>Self-identified stage:</b> {stage} &nbsp;&nbsp; '
    f'<b>Your map position:</b> {map_stage}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<span class="pill">{business_type}</span>'
    f'<span class="pill">Concern: {concern}</span>',
    unsafe_allow_html=True,
)

# -----------------------------
# Four-stage X/Y matrix
# -----------------------------
fig = go.Figure()

# Stage backgrounds. These are deliberately light so the result marker
# and the benchmark zone remain the strongest visual signals.
stage_regions = [
    # x0, x1, y0, y1, fill
    (0, cut, 0, cut, "rgba(236, 214, 203, 0.42)"),   # Starting
    (0, cut, cut, 10, "rgba(201, 228, 199, 0.46)"),  # Growing
    (cut, 10, cut, 10, "rgba(205, 221, 244, 0.50)"), # Established
    (cut, 10, 0, cut, "rgba(239, 212, 205, 0.42)"),  # Fixing
]

for x0, x1, y0, y1, fill in stage_regions:
    fig.add_shape(
        type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
        fillcolor=fill,
        line=dict(width=0),
        layer="below",
    )

# True X/Y axes.
base_line = "rgba(51,65,85,0.70)"
fig.add_shape(
    type="line", x0=0, x1=10.15, y0=0, y1=0,
    line=dict(color=base_line, width=1.1)
)
fig.add_shape(
    type="line", x0=0, x1=0, y0=0, y1=10.15,
    line=dict(color=base_line, width=1.1)
)

# Quadrant dividers.
quad_line = "rgba(100,116,139,0.42)"
fig.add_shape(
    type="line", x0=cut, x1=cut, y0=0, y1=10,
    line=dict(color=quad_line, width=0.9)
)
fig.add_shape(
    type="line", x0=0, x1=10, y0=cut, y1=cut,
    line=dict(color=quad_line, width=0.9)
)

# Expected benchmark zone based on business type + self-identified stage.
fig.add_shape(
    type="rect",
    x0=x_range[0], x1=x_range[1],
    y0=y_range[0], y1=y_range[1],
    fillcolor="rgba(107,114,128,0.34)",
    line=dict(color="rgba(75,85,99,0.72)", width=1.0, dash="dot"),
)
fig.add_annotation(
    x=(x_range[0] + x_range[1]) / 2,
    y=(y_range[0] + y_range[1]) / 2,
    xanchor="center",
    yanchor="middle",
    align="center",
    text="<b>You should be here</b>",
    showarrow=False,
    font=dict(size=10.5, color="#1F2937"),
    bgcolor="rgba(229,231,235,0.76)",
    bordercolor="rgba(75,85,99,0.0)",
    borderpad=1.5,
)

# Reader position at the true X/Y coordinates.
pin_text_y = max(0.35, y_score - 0.62)
fig.add_trace(
    go.Scatter(
        x=[x_score],
        y=[y_score],
        mode="text",
        text=["📍"],
        textfont=dict(size=21, color="#C53030"),
        hovertemplate=(
            f"Market Reach: {x_score:.1f}<br>"
            f"Operational Maturity: {y_score:.1f}<extra></extra>"
        ),
        showlegend=False,
    )
)
fig.add_annotation(
    x=x_score,
    y=pin_text_y,
    text="<b>Your position</b>",
    showarrow=False,
    font=dict(size=12, color="#C53030"),
)

# Stage labels + their plain-English descriptor.
# Positioned toward the outer corners so they do not compete with the benchmark box.
def add_stage_label(x, y, stage_name, descriptor, xanchor):
    fig.add_annotation(
        x=x,
        y=y,
        text=(
            f"<b>{stage_name}</b><br>"
            f"<span style='font-size:10px'>{descriptor}</span>"
        ),
        showarrow=False,
        xanchor=xanchor,
        yanchor="top",
        align="left",
        font=dict(size=13, color="#475569"),
    )


add_stage_label(0.55, 9.55, "Growing", "Ready for more customers", "left")
add_stage_label(9.45, 9.55, "Established", "In balance", "right")
add_stage_label(0.55, 4.55, "Starting", "Building the base", "left")
add_stage_label(9.45, 4.55, "Fixing", "Growing pains", "right")

# Axis titles.
fig.add_annotation(
    x=0.5,
    y=-0.14,
    xref="paper",
    yref="paper",
    text=(
        "<b>Market reach</b><br>"
        "<span style='font-size:10px'>(more ways customers can find and buy from you)</span>"
    ),
    showarrow=False,
    align="center",
    font=dict(size=11.5, color="#64748B"),
)
fig.add_annotation(
    x=-0.06,
    y=0.5,
    xref="paper",
    yref="paper",
    text=(
        "<b>Operational maturity</b><br>"
        "<span style='font-size:10px'>(more repeatable systems)</span>"
    ),
    showarrow=False,
    textangle=-90,
    align="center",
    font=dict(size=11.5, color="#64748B"),
)

fig.update_layout(
    height=420,
    margin=dict(l=102, r=40, t=26, b=84),
    paper_bgcolor="white",
    plot_bgcolor="#FCFCFB",
    xaxis=dict(
        range=[0, 10.5],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title="",
        fixedrange=True,
    ),
    yaxis=dict(
        range=[0, 10.5],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title="",
        fixedrange=True,
    ),
    hoverlabel=dict(bgcolor="white", font_size=12),
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False, "responsive": True},
)

# -----------------------------
# Results
# -----------------------------
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        f'<div class="result-card"><div class="result-label">Market Reach</div>'
        f'<div class="result-value">{x_label}</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="result-card"><div class="result-label">Operational Maturity</div>'
        f'<div class="result-value">{y_label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(f"### Your stage fit: **{stage_fit}**")
st.write(stage_comparison)
st.write(interpretation)
st.caption(perceived_note)
st.markdown(
    f'<div class="next-move"><b>Next move:</b> {next_move}</div>',
    unsafe_allow_html=True,
)

with st.expander("What this map is measuring"):
    st.write(
        "Market Reach reflects the breadth and diversity of how customers find and buy from you. "
        "Operational Maturity reflects the repeatability of the systems that support delivery. "
        "The four regions translate those two signals into a broad business-stage pattern. "
        "The grey benchmark zone compares your current position with the expected range for your "
        "business type and the stage you selected."
    )

st.divider()
st.caption("Prototype testing controls")
with st.expander("Try another result"):
    business_types = ["Product", "Service", "Content", "Local", "Hybrid"]
    stages = ["Starting", "Growing", "Established", "Fixing"]
    concerns = ["Money", "Getting customers", "Keeping customers", "Working smarter"]

    demo_type = st.selectbox(
        "Business type",
        business_types,
        index=business_types.index(business_type) if business_type in business_types else 0,
    )
    demo_stage = st.selectbox(
        "Stage",
        stages,
        index=stages.index(stage) if stage in stages else 1,
    )
    demo_concern = st.selectbox(
        "Concern",
        concerns,
        index=concerns.index(concern) if concern in concerns else 0,
    )
    demo_x = st.slider("Market Reach", 0.0, 10.0, float(x_score), 0.1)
    demo_y = st.slider("Operational Maturity", 0.0, 10.0, float(y_score), 0.1)

    url = (
        f"?type={quote(demo_type)}&stage={quote(demo_stage)}&"
        f"concern={quote(demo_concern)}&x={demo_x}&y={demo_y}"
    )
    st.code(url)
    st.markdown(f"[Open this result]({url})")

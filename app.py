import streamlit as st
import plotly.graph_objects as go
from urllib.parse import quote
from html import escape

st.set_page_config(page_title="Business Stage Map", page_icon="📍", layout="wide")

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {max-width: 1320px; padding-top: 2.4rem; padding-bottom: 0.8rem;}
    h1, h2, h3 {letter-spacing: -0.02em;}
    .hero-title {font-size: 2.05rem; font-weight: 800; line-height:1.15; margin: 0 0 0.35rem 0; padding-top:0.15rem;}
    .meta {font-size: 0.98rem; color:#374151; margin-bottom: 0.25rem;}
    .pill {display:inline-block; padding:0.3rem 0.65rem; border-radius:999px; background:#F3F4F6; margin-right:0.35rem; margin-bottom:0.25rem; font-weight:600; font-size:0.86rem;}
    .summary-card {padding:1.0rem 1.05rem 0.95rem 1.05rem; border-radius:15px; border:1px solid #E5E7EB; background:#FFFFFF; box-shadow:0 8px 24px rgba(17,24,39,0.05); margin-top:-1.75rem;}
    .summary-kicker {font-size:0.70rem; text-transform:uppercase; letter-spacing:0.09em; color:#6B7280; font-weight:800; margin-bottom:0.45rem;}
    .dash-item {padding:0.72rem 0 0.74rem 0; border-bottom:1px solid #E9EDF2;}
    .dash-item:last-of-type {border-bottom:none;}
    .dash-label {font-size:0.68rem; text-transform:uppercase; letter-spacing:0.06em; color:#6B7280; font-weight:800; margin-bottom:0.34rem;}
    .dash-value {font-size:0.88rem; line-height:1.36; color:#1F2937; font-weight:650;}
    .answer-chip {display:inline-block; padding:0.22rem 0.48rem; margin:0 0.22rem 0.22rem 0; border-radius:999px; background:#F3F4F6; border:1px solid #E5E7EB; color:#263244; font-size:0.76rem; line-height:1.25; font-weight:650;}
    .systems-value {font-size:1.0rem; color:#111827; font-weight:750;}
    .result-wrap {border-top:1px solid #E5E7EB; margin-top:0.48rem; padding-top:0.72rem;}
    .result-label {font-size:0.68rem; text-transform:uppercase; letter-spacing:0.06em; color:#6B7280; font-weight:800; margin-bottom:0.28rem;}
    .result-line {font-size:0.88rem; line-height:1.43; color:#1F2937; margin:0;}
    .summary-disclaimer {font-size:0.70rem; line-height:1.42; color:#7A818D; font-style:italic; margin:0.72rem 0 0 0; padding-top:0.66rem; border-top:1px solid #F0F2F5;}
    div[data-testid="stPlotlyChart"] {margin-top:-0.2rem;}
    
.disclaimer-under-chart {
    margin-top: -34px;
    margin-left: 92px;
    margin-right: 24px;
    padding: 0;
    font-size: 0.76rem;
    line-height: 1.38;
    color: #6b7280;
    font-style: italic;
    box-sizing: border-box;
}

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


def split_multi(value):
    """Turn a Tally multi-select value into a clean display list."""
    if isinstance(value, list):
        raw_items = value
    else:
        text = str(value or "").strip()
        if not text:
            return []
        # Be forgiving if literal square brackets were accidentally added
        # around a Tally @mention in the redirect URL.
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1].strip()
        # Tally/browser encodings can vary; support common separators.
        for sep in ("|", ";", "\n"):
            if sep in text:
                raw_items = text.split(sep)
                break
        else:
            raw_items = text.split(",")
    return [str(item).strip().strip("[]") for item in raw_items if str(item).strip()]


find_answers = split_multi(q("find", ""))
buy_answers = split_multi(q("buy", ""))
systems_answer = str(q("systems", "")).strip()

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
# Visual position mapping
# -----------------------------
# Keep the assessment itself on the true 0–10 scale, but inset plotted
# positions so a minimum or maximum result never sits on a chart boundary.
# This mapping preserves the midpoint exactly: 0 -> 1, 5 -> 5, 10 -> 9.
def display_coord(score):
    return 1.0 + (float(score) * 0.8)

x_plot = display_coord(x_score)
y_plot = display_coord(y_score)

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

# Transform the benchmark box using the same visual mapping as the reader pin.
x_range_plot = (display_coord(x_range[0]), display_coord(x_range[1]))
y_range_plot = (display_coord(y_range[0]), display_coord(y_range[1]))

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


# -----------------------------
# Compact dashboard interpretation
# -----------------------------
# The numerical scores remain internal. The reader sees the actual answers
# that produced the map position, which is easier to understand and avoids
# implying false precision.

def answer_text(items, fallback):
    if not items:
        return fallback
    return " · ".join(items)


def answer_chips(items, fallback):
    if not items:
        return f'<span class="answer-chip">{escape(fallback)}</span>'
    return "".join(
        f'<span class="answer-chip">{escape(str(item))}</span>'
        for item in items
    )


find_display = answer_chips(find_answers, "Answer not received")
buy_display = answer_chips(buy_answers, "Answer not received")
systems_display = escape(systems_answer.strip("[]") or "Answer not received")

if stage == map_stage:
    conclusion = (
        f"You chose <b>{stage}</b>. The ways customers find and buy from you, together with the "
        f"repeatable systems you already have, also place you in the <b>{map_stage}</b> area of this map."
    )
else:
    conclusion = (
        f"You chose <b>{stage}</b>. The ways customers find and buy from you, together with the "
        f"repeatable systems you already have, place you closer to <b>{map_stage}</b> on this map."
    )

disclaimer = (
    "This is a simple visual guide to help you think about your business, not a final assessment. "
    "Other factors not covered here may change the picture."
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
    (0, cut, 0, cut, "rgba(226, 238, 223, 0.52)"),   # Starting — green
    (0, cut, cut, 10, "rgba(246, 239, 201, 0.50)"),  # Growing — yellow
    (cut, 10, cut, 10, "rgba(232, 225, 242, 0.52)"), # Established — purple
    (cut, 10, 0, cut, "rgba(242, 226, 211, 0.50)"),  # Fixing — orange
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
    x0=x_range_plot[0], x1=x_range_plot[1],
    y0=y_range_plot[0], y1=y_range_plot[1],
    fillcolor="rgba(107,114,128,0.34)",
    line=dict(color="rgba(75,85,99,0.72)", width=1.0, dash="dot"),
)
fig.add_annotation(
    x=(x_range_plot[0] + x_range_plot[1]) / 2,
    y=(y_range_plot[0] + y_range_plot[1]) / 2,
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

# Reader position. The tooltip shows the true score; the plotted location uses
# the inset visual coordinates so the pin never touches the outer boundary.
pin_text_y = max(0.35, y_plot - 0.62)
fig.add_trace(
    go.Scatter(
        x=[x_plot],
        y=[y_plot],
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
    x=x_plot,
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
    height=390,
    margin=dict(l=92, r=24, t=20, b=76),
    paper_bgcolor="white",
    plot_bgcolor="#FCFCFB",
    xaxis=dict(
        range=[0, 10.25],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title="",
        fixedrange=True,
    ),
    yaxis=dict(
        range=[0, 10.25],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title="",
        fixedrange=True,
    ),
    hoverlabel=dict(bgcolor="white", font_size=12),
)

# -----------------------------
# Map + interpretation in one view
# -----------------------------
left, right = st.columns([2.35, 1.0], gap="large")

with left:
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )
    st.markdown(
        """
        <div class="disclaimer-under-chart">
            This is a simple visual guide to help you think about your business, not a final assessment.
            Other factors not covered here may change the picture.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    # Keep HTML flush-left. Markdown treats indented HTML as a code block,
    # which is why the previous version displayed the <div> tags literally.
    dashboard_html = f"""<div class="summary-card">
<div class="summary-kicker">Your answers at a glance</div>
<div class="dash-item">
<div class="dash-label">How customers find you</div>
<div class="dash-value">{find_display}</div>
</div>
<div class="dash-item">
<div class="dash-label">How customers buy</div>
<div class="dash-value">{buy_display}</div>
</div>
<div class="dash-item">
<div class="dash-label">Repeatable systems</div>
<div class="systems-value">{systems_display}</div>
</div>
<div class="result-wrap">
<div class="result-label">What this suggests</div>
<p class="result-line">{conclusion}</p>
</div>
</div>"""
    st.markdown(dashboard_html, unsafe_allow_html=True)

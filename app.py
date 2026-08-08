import io
import re
from html import escape, unescape

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image, ImageDraw, ImageFont


st.set_page_config(
    page_title="Business Stage Map",
    page_icon="📍",
    layout="wide",
)


# =========================================================
# STYLING
# =========================================================
st.markdown(
    """
    <style>

    .block-container {
        max-width: 1320px;
        padding-top: 2.2rem;
        padding-bottom: 0.8rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    .hero-title {
        font-size: 2.05rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
        padding: 0.08rem 0 0 0;
        white-space: nowrap;
    }

    .meta {
        font-size: 0.98rem;
        color: #374151;
        margin-top: 0.35rem;
        margin-bottom: 0.25rem;
    }

    .meta-line {
        display: block;
        margin-bottom: 0.15rem;
    }

    .pill {
        display: inline-block;
        padding: 0.3rem 0.65rem;
        border-radius: 999px;
        background: #F3F4F6;
        margin-right: 0.35rem;
        margin-bottom: 0.25rem;
        font-weight: 600;
        font-size: 0.86rem;
    }

    .map-logic {
        font-size: 0.76rem;
        line-height: 1.42;
        color: #6B7280;
        margin: 0.72rem 0 0.15rem 0;
        max-width: 920px;
    }

    .map-logic b {
        color: #4B5563;
    }

    .summary-card {
        padding: 0.78rem 0.82rem 0.76rem 0.82rem;
        border-radius: 14px;
        border: 1px solid #E5E7EB;
        background: #FFFFFF;
        box-shadow: 0 8px 24px rgba(17,24,39,0.05);
        margin-top: -1.75rem;
    }

    .summary-kicker {
        font-size: 0.64rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #6B7280;
        font-weight: 800;
        margin-bottom: 0.45rem;
    }

    .dash-item {
        padding: 0.56rem 0 0.58rem 0;
        border-bottom: 1px solid #E9EDF2;
    }

    .dash-item:last-of-type {
        border-bottom: none;
    }

    .dash-label {
        font-size: 0.63rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6B7280;
        font-weight: 800;
        margin-bottom: 0.34rem;
    }

    .dash-value {
        font-size: 0.82rem;
        line-height: 1.36;
        color: #1F2937;
        font-weight: 650;
    }

    .answer-chip {
        display: inline-block;
        padding: 0.18rem 0.42rem;
        margin: 0 0.22rem 0.22rem 0;
        border-radius: 999px;
        background: #F3F4F6;
        border: 1px solid #E5E7EB;
        color: #263244;
        font-size: 0.72rem;
        line-height: 1.22;
        font-weight: 650;
    }

    .systems-value {
        font-size: 0.92rem;
        color: #111827;
        font-weight: 750;
    }

    .result-wrap {
        border-top: 1px solid #E5E7EB;
        margin-top: 0.38rem;
        padding-top: 0.56rem;
    }

    .result-label {
        font-size: 0.63rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6B7280;
        font-weight: 800;
        margin-bottom: 0.28rem;
    }

    .result-line {
        font-size: 0.82rem;
        line-height: 1.38;
        color: #1F2937;
        margin: 0;
    }

    div[data-testid="stPlotlyChart"] {
        margin-top: -0.2rem;
        margin-bottom: 0 !important;
    }


    /* =====================================================
       DISCLAIMER
       Keep it tucked directly beneath the x-axis so it stays
       visible in the first screen, but do not clip the text.
       ===================================================== */

    .disclaimer-under-chart {
        margin-top: -19px;
        margin-left: 78px;
        margin-right: 12px;
        margin-bottom: 0.25rem;
        padding: 0;
        font-size: 0.74rem;
        line-height: 1.38;
        color: #6B7280;
        font-style: italic;
        box-sizing: border-box;
        position: relative;
        z-index: 2;
    }


    /* =====================================================
       SMALL WHITE SAVE BUTTON BESIDE TITLE
       ===================================================== */

    div[data-testid="stDownloadButton"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stDownloadButton"] > div {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stDownloadButton"] button {
        background: #FFFFFF !important;
        color: #374151 !important;

        border: 1px solid #D8DEE7 !important;
        border-radius: 999px !important;

        min-height: 34px !important;
        height: 34px !important;

        width: auto !important;
        min-width: 138px !important;

        padding: 0 0.82rem !important;

        font-size: 0.76rem !important;
        font-weight: 700 !important;
        line-height: 1 !important;

        white-space: nowrap !important;

        box-shadow: 0 2px 7px rgba(17,24,39,0.06) !important;

        transition:
            background-color 0.15s ease,
            border-color 0.15s ease,
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    div[data-testid="stDownloadButton"] button p {
        white-space: nowrap !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background: #F8FAFC !important;
        color: #111827 !important;
        border-color: #BBC3CE !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(17,24,39,0.09) !important;
    }

    div[data-testid="stDownloadButton"] button:active {
        transform: translateY(0);
        box-shadow: 0 2px 5px rgba(17,24,39,0.06) !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# QUERY PARAMS
# =========================================================
qp = st.query_params


def q(name, default):
    val = qp.get(name, default)

    if isinstance(val, list):
        return val[0]

    return val


def short_answer(value):
    text = str(value).replace("+", " ").strip()

    for separator in (" — ", " – ", " - "):
        if separator in text:
            text = text.split(separator, 1)[0].strip()
            break

    return text


business_type = short_answer(
    q("type", "Product")
).title()

stage = short_answer(
    q("stage", "Growing")
).title()

concern = short_answer(
    q("concern", "Getting customers")
)


def split_multi(value):
    """Turn a Tally multi-select value into a clean display list."""

    if isinstance(value, list):
        raw_items = value

    else:
        text = str(value or "").strip()

        if not text:
            return []

        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1].strip()

        for sep in ("|", ";", "\n"):
            if sep in text:
                raw_items = text.split(sep)
                break
        else:
            raw_items = text.split(",")

    return [
        str(item).strip().strip("[]")
        for item in raw_items
        if str(item).strip()
    ]


find_answers = split_multi(
    q("find", "")
)

buy_answers = split_multi(
    q("buy", "")
)

systems_answer = str(
    q("systems", "")
).strip()


try:
    x_score = float(
        q("x", 7.2)
    )
except Exception:
    x_score = 7.2


try:
    y_score = float(
        q("y", 4.5)
    )
except Exception:
    y_score = 4.5


if x_score > 10:
    x_score = x_score / 10

if y_score > 10:
    y_score = y_score / 10


x_score = max(
    0,
    min(10, x_score)
)

y_score = max(
    0,
    min(10, y_score)
)


# =========================================================
# VISUAL POSITION MAPPING
# =========================================================
def display_coord(score):
    return 1.0 + (
        float(score) * 0.8
    )


x_plot = display_coord(
    x_score
)

y_plot = display_coord(
    y_score
)


# =========================================================
# BENCHMARKS
# =========================================================
benchmarks = {

    ("Product", "Starting"):
        ((2.0, 4.5), (1.5, 4.5)),

    ("Product", "Growing"):
        ((5.0, 7.5), (4.5, 7.0)),

    ("Product", "Established"):
        ((7.0, 10.0), (6.5, 10.0)),


    ("Service", "Starting"):
        ((2.0, 4.5), (1.5, 4.5)),

    ("Service", "Growing"):
        ((4.5, 6.5), (4.0, 6.5)),

    ("Service", "Established"):
        ((6.5, 9.0), (6.5, 10.0)),


    ("Content", "Starting"):
        ((2.0, 4.5), (1.5, 4.5)),

    ("Content", "Growing"):
        ((5.0, 7.5), (4.0, 6.5)),

    ("Content", "Established"):
        ((7.5, 10.0), (6.5, 10.0)),


    ("Local", "Starting"):
        ((2.5, 5.0), (2.0, 5.0)),

    ("Local", "Growing"):
        ((5.5, 7.5), (5.0, 7.5)),

    ("Local", "Established"):
        ((7.0, 10.0), (7.0, 10.0)),


    ("Hybrid", "Starting"):
        ((2.5, 5.0), (2.0, 5.0)),

    ("Hybrid", "Growing"):
        ((5.5, 8.0), (5.0, 7.5)),

    ("Hybrid", "Established"):
        ((7.0, 10.0), (7.0, 10.0)),
}


benchmark_stage = (
    "Growing"
    if stage == "Fixing"
    else stage
)


x_range, y_range = benchmarks.get(
    (
        business_type,
        benchmark_stage
    ),
    (
        (4.5, 7.5),
        (4.5, 7.5)
    )
)


x_range_plot = (
    display_coord(x_range[0]),
    display_coord(x_range[1])
)

y_range_plot = (
    display_coord(y_range[0]),
    display_coord(y_range[1])
)


# =========================================================
# LABELS AND DIAGNOSTICS
# =========================================================
def level(score, axis):

    if score < 3.5:
        return "Early"

    if score < 5.5:
        return "Developing"

    if score < 7.5:
        return "Strong"

    return (
        "Broad"
        if axis == "x"
        else "Mature"
    )


x_label = level(
    x_score,
    "x"
)

y_label = level(
    y_score,
    "y"
)


cut = 5.0


if (
    x_score < cut
    and
    y_score < cut
):
    map_stage = "Starting"
    map_descriptor = "Building the base"

elif (
    x_score < cut
    and
    y_score >= cut
):
    map_stage = "Growing"
    map_descriptor = "Ready for more customers"

elif (
    x_score >= cut
    and
    y_score >= cut
):
    map_stage = "Established"
    map_descriptor = "In balance"

else:
    map_stage = "Fixing"
    map_descriptor = "Growing pains"


# =========================================================
# DASHBOARD INTERPRETATION
# =========================================================
def answer_chips(items, fallback):

    if not items:
        return (
            f'<span class="answer-chip">'
            f'{escape(fallback)}'
            f'</span>'
        )

    return "".join(
        (
            f'<span class="answer-chip">'
            f'{escape(str(item))}'
            f'</span>'
        )
        for item in items
    )


find_display = answer_chips(
    find_answers,
    "Answer not received"
)

buy_display = answer_chips(
    buy_answers,
    "Answer not received"
)

systems_display = escape(
    systems_answer.strip("[]")
    or
    "Answer not received"
)


stage_order = {
    "Starting": 0,
    "Growing": 1,
    "Established": 2,
}


if stage == map_stage:

    conclusion = (
        f"You chose <b>{stage}</b>, and your answers point "
        f"to the same place on the map. "
        f"Your customer reach and repeatable systems are "
        f"broadly in line with a <b>{stage}</b> business."
    )

elif map_stage == "Fixing":

    conclusion = (
        f"You chose <b>{stage}</b>. Customers can find and "
        f"buy from you in several ways, but your repeatable "
        f"systems are not keeping pace. That moves you toward "
        f"<b>Fixing</b>, where growth can start putting strain "
        f"on the business."
    )

elif stage == "Fixing":

    conclusion = (
        f"You chose <b>Fixing</b>, but your current answers "
        f"place you closer to <b>{map_stage}</b>. "
        f"Your customer reach and repeatable systems look "
        f"stronger than a typical fixing position on this map."
    )

elif (
    stage in stage_order
    and
    map_stage in stage_order
    and
    stage_order[map_stage] > stage_order[stage]
):

    conclusion = (
        f"You chose <b>{stage}</b>. Your answers show wider "
        f"customer reach and more repeatable systems than that "
        f"stage usually suggests, so you sit closer to "
        f"<b>{map_stage}</b> on this map."
    )

elif (
    stage in stage_order
    and
    map_stage in stage_order
    and
    stage_order[map_stage] < stage_order[stage]
):

    conclusion = (
        f"You chose <b>{stage}</b>. Your answers show fewer "
        f"customer routes and less-developed repeatable systems "
        f"than that stage usually needs, so you sit closer to "
        f"<b>{map_stage}</b>. That gap is worth looking at."
    )

else:

    conclusion = (
        f"You chose <b>{stage}</b>, while your answers place "
        f"you closer to <b>{map_stage}</b> on this map. "
        f"The difference is a useful prompt to look more closely "
        f"at your customer reach and systems."
    )


disclaimer = (
    "This is a simple visual guide to help you think about your "
    "business, not a final assessment. Other factors not covered "
    "here may change the picture."
)


# =========================================================
# PNG HELPER FUNCTIONS
# =========================================================
def strip_html_tags(text):

    return unescape(
        re.sub(
            r"<[^>]+>",
            "",
            text or ""
        )
    ).strip()


def load_font(size=18, bold=False):

    if bold:

        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]

    else:

        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/Library/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]


    for path in candidates:

        try:

            return ImageFont.truetype(
                path,
                size=size
            )

        except Exception:

            pass


    return ImageFont.load_default()


def text_size(draw, text, font):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    return (
        bbox[2] - bbox[0],
        bbox[3] - bbox[1]
    )


def wrap_text_to_width(
    draw,
    text,
    font,
    max_width
):

    words = str(text).split()

    if not words:
        return [""]

    lines = []
    current = words[0]

    for word in words[1:]:

        trial = current + " " + word

        width, _ = text_size(
            draw,
            trial,
            font
        )

        if width <= max_width:

            current = trial

        else:

            lines.append(
                current
            )

            current = word

    lines.append(
        current
    )

    return lines


def draw_wrapped_text(
    draw,
    text,
    xy,
    font,
    fill,
    max_width,
    line_gap=6
):

    x, y = xy

    lines = []

    for paragraph in str(text).split("\n"):

        wrapped = wrap_text_to_width(
            draw,
            paragraph,
            font,
            max_width
        )

        lines.extend(
            wrapped
            if wrapped
            else [""]
        )


    if hasattr(font, "getmetrics"):

        ascent, descent = font.getmetrics()

    else:

        ascent = getattr(
            font,
            "size",
            18
        )

        descent = 0


    line_height = (
        ascent
        +
        descent
        +
        line_gap
    )


    for line in lines:

        draw.text(
            (x, y),
            line,
            font=font,
            fill=fill
        )

        y += line_height


    return y


def draw_pill(
    draw,
    x,
    y,
    text,
    font,
    bg="#F3F4F6",
    fg="#374151",
    outline="#E5E7EB"
):

    pad_x = 16
    pad_y = 8

    tw, th = text_size(
        draw,
        text,
        font
    )

    width = (
        tw
        +
        (pad_x * 2)
    )

    height = (
        th
        +
        (pad_y * 2)
        -
        2
    )

    draw.rounded_rectangle(
        (
            x,
            y,
            x + width,
            y + height
        ),
        radius=18,
        fill=bg,
        outline=outline,
        width=1
    )

    draw.text(
        (
            x + pad_x,
            y + pad_y - 2
        ),
        text,
        font=font,
        fill=fg
    )

    return (
        x
        +
        width
        +
        10
    )


def build_result_png(
    fig,
    stage,
    map_stage,
    business_type,
    concern,
    find_answers,
    buy_answers,
    systems_answer,
    conclusion_html,
    disclaimer_text
):

    chart_bytes = pio.to_image(
        fig,
        format="png",
        width=1600,
        height=980,
        scale=2
    )

    chart_img = Image.open(
        io.BytesIO(
            chart_bytes
        )
    ).convert(
        "RGBA"
    )

    canvas_w = 1900
    canvas_h = 1350

    background = Image.new(
        "RGB",
        (
            canvas_w,
            canvas_h
        ),
        "white"
    )

    draw = ImageDraw.Draw(
        background
    )

    font_title = load_font(
        44,
        bold=True
    )

    font_meta_bold = load_font(
        22,
        bold=True
    )

    font_meta = load_font(
        22
    )

    font_pill = load_font(
        18,
        bold=True
    )

    font_logic_bold = load_font(
        16,
        bold=True
    )

    font_logic = load_font(
        16
    )

    font_card_kicker = load_font(
        14,
        bold=True
    )

    font_card_label = load_font(
        14,
        bold=True
    )

    font_card_value = load_font(
        20,
        bold=True
    )

    font_card_body = load_font(
        18
    )

    font_small = load_font(
        15
    )

    left_x = 70
    left_w = 1080

    right_x = 1180
    right_w = 650

    top_y = 60

    draw.text(
        (
            left_x,
            top_y
        ),
        "Your Business Stage Map",
        font=font_title,
        fill="#111827"
    )

    y = top_y + 68

    draw.text(
        (
            left_x,
            y
        ),
        "You think you're at:",
        font=font_meta_bold,
        fill="#374151"
    )

    width1, _ = text_size(
        draw,
        "You think you're at:",
        font_meta_bold
    )

    draw.text(
        (
            left_x
            +
            width1
            +
            10,
            y
        ),
        stage,
        font=font_meta,
        fill="#374151"
    )

    y += 34

    draw.text(
        (
            left_x,
            y
        ),
        "Your answers show:",
        font=font_meta_bold,
        fill="#374151"
    )

    width2, _ = text_size(
        draw,
        "Your answers show:",
        font_meta_bold
    )

    draw.text(
        (
            left_x
            +
            width2
            +
            10,
            y
        ),
        map_stage,
        font=font_meta,
        fill="#374151"
    )

    y += 46

    px = left_x

    px = draw_pill(
        draw,
        px,
        y,
        business_type,
        font_pill
    )

    px = draw_pill(
        draw,
        px,
        y,
        f"Concern: {concern}",
        font_pill
    )

    y += 52

    logic_prefix = (
        "How this map works:"
    )

    logic_rest = (
        "Your position is based on how customers find and buy from you "
        "(questions 5–6) and how repeatable your systems are (question 7). "
        "The benchmark is based on the stage you selected (question 3)."
    )

    draw.text(
        (
            left_x,
            y
        ),
        logic_prefix,
        font=font_logic_bold,
        fill="#4B5563"
    )

    prefix_width, _ = text_size(
        draw,
        logic_prefix,
        font_logic_bold
    )

    draw_wrapped_text(
        draw,
        logic_rest,
        (
            left_x
            +
            prefix_width
            +
            8,
            y
        ),
        font_logic,
        "#6B7280",
        left_w
        -
        prefix_width
        -
        8,
        line_gap=4
    )

    y += 42

    chart_copy = chart_img.copy()

    chart_copy.thumbnail(
        (
            left_w,
            760
        )
    )

    background.paste(
        chart_copy,
        (
            left_x,
            y
        ),
        chart_copy
    )

    chart_bottom = (
        y
        +
        chart_copy.size[1]
    )

    draw_wrapped_text(
        draw,
        disclaimer_text,
        (
            left_x
            +
            78,
            chart_bottom
            +
            2
        ),
        font_small,
        "#6B7280",
        left_w
        -
        90,
        line_gap=4
    )

    card_x = right_x
    card_y = 145
    card_w = right_w
    card_h = 830

    draw.rounded_rectangle(
        (
            card_x,
            card_y,
            card_x
            +
            card_w,
            card_y
            +
            card_h
        ),
        radius=24,
        fill="white",
        outline="#E5E7EB",
        width=2
    )

    inner_x = (
        card_x
        +
        28
    )

    inner_y = (
        card_y
        +
        26
    )

    inner_w = (
        card_w
        -
        56
    )

    draw.text(
        (
            inner_x,
            inner_y
        ),
        "YOUR ANSWERS AT A GLANCE",
        font=font_card_kicker,
        fill="#6B7280"
    )

    inner_y += 40

    draw.text(
        (
            inner_x,
            inner_y
        ),
        "HOW CUSTOMERS FIND YOU",
        font=font_card_label,
        fill="#6B7280"
    )

    inner_y += 24

    find_text = (
        " · ".join(
            find_answers
        )
        if find_answers
        else
        "Answer not received"
    )

    inner_y = draw_wrapped_text(
        draw,
        find_text,
        (
            inner_x,
            inner_y
        ),
        font_card_body,
        "#1F2937",
        inner_w,
        line_gap=5
    )

    inner_y += 14

    draw.line(
        (
            inner_x,
            inner_y,
            inner_x
            +
            inner_w,
            inner_y
        ),
        fill="#E9EDF2",
        width=1
    )

    inner_y += 18

    draw.text(
        (
            inner_x,
            inner_y
        ),
        "HOW CUSTOMERS BUY",
        font=font_card_label,
        fill="#6B7280"
    )

    inner_y += 24

    buy_text = (
        " · ".join(
            buy_answers
        )
        if buy_answers
        else
        "Answer not received"
    )

    inner_y = draw_wrapped_text(
        draw,
        buy_text,
        (
            inner_x,
            inner_y
        ),
        font_card_body,
        "#1F2937",
        inner_w,
        line_gap=5
    )

    inner_y += 14

    draw.line(
        (
            inner_x,
            inner_y,
            inner_x
            +
            inner_w,
            inner_y
        ),
        fill="#E9EDF2",
        width=1
    )

    inner_y += 18

    draw.text(
        (
            inner_x,
            inner_y
        ),
        "REPEATABLE SYSTEMS",
        font=font_card_label,
        fill="#6B7280"
    )

    inner_y += 24

    systems_text = (
        systems_answer.strip("[]")
        or
        "Answer not received"
    )

    inner_y = draw_wrapped_text(
        draw,
        systems_text,
        (
            inner_x,
            inner_y
        ),
        font_card_value,
        "#111827",
        inner_w,
        line_gap=5
    )

    inner_y += 14

    draw.line(
        (
            inner_x,
            inner_y,
            inner_x
            +
            inner_w,
            inner_y
        ),
        fill="#E9EDF2",
        width=1
    )

    inner_y += 18

    draw.text(
        (
            inner_x,
            inner_y
        ),
        "WHAT THIS SUGGESTS",
        font=font_card_label,
        fill="#6B7280"
    )

    inner_y += 24

    conclusion_plain = strip_html_tags(
        conclusion_html
    )

    draw_wrapped_text(
        draw,
        conclusion_plain,
        (
            inner_x,
            inner_y
        ),
        font_card_body,
        "#1F2937",
        inner_w,
        line_gap=6
    )

    output = io.BytesIO()

    background.save(
        output,
        format="PNG"
    )

    output.seek(
        0
    )

    return output.getvalue()


# =========================================================
# BUILD BUSINESS STAGE MAP
# =========================================================
fig = go.Figure()


stage_regions = [

    (
        0,
        cut,
        0,
        cut,
        "rgba(226, 238, 223, 0.52)"
    ),

    (
        0,
        cut,
        cut,
        10,
        "rgba(246, 239, 201, 0.50)"
    ),

    (
        cut,
        10,
        cut,
        10,
        "rgba(232, 225, 242, 0.52)"
    ),

    (
        cut,
        10,
        0,
        cut,
        "rgba(242, 226, 211, 0.50)"
    ),
]


for (
    x0,
    x1,
    y0,
    y1,
    fill
) in stage_regions:

    fig.add_shape(
        type="rect",
        x0=x0,
        x1=x1,
        y0=y0,
        y1=y1,
        fillcolor=fill,
        line=dict(
            width=0
        ),
        layer="below"
    )


base_line = (
    "rgba(51,65,85,0.70)"
)


fig.add_shape(
    type="line",
    x0=0,
    x1=10.15,
    y0=0,
    y1=0,
    line=dict(
        color=base_line,
        width=1.1
    )
)


fig.add_shape(
    type="line",
    x0=0,
    x1=0,
    y0=0,
    y1=10.15,
    line=dict(
        color=base_line,
        width=1.1
    )
)


quad_line = (
    "rgba(100,116,139,0.42)"
)


fig.add_shape(
    type="line",
    x0=cut,
    x1=cut,
    y0=0,
    y1=10,
    line=dict(
        color=quad_line,
        width=0.9
    )
)


fig.add_shape(
    type="line",
    x0=0,
    x1=10,
    y0=cut,
    y1=cut,
    line=dict(
        color=quad_line,
        width=0.9
    )
)


benchmark_colors = {

    "Starting": {
        "line": "#2F343B",
        "fill": "rgba(120,168,120,0.12)"
    },

    "Growing": {
        "line": "#2F343B",
        "fill": "rgba(185,154,54,0.12)"
    },

    "Established": {
        "line": "#2F343B",
        "fill": "rgba(138,114,180,0.12)"
    },

    "Fixing": {
        "line": "#2F343B",
        "fill": "rgba(197,125,72,0.12)"
    },
}


benchmark_color = benchmark_colors.get(
    stage,
    benchmark_colors["Growing"]
)


benchmark_label = (
    f"Stability range: {stage}"
    if stage == "Fixing"
    else
    f"Expected range: {stage}"
)


benchmark_cx = (
    x_range_plot[0]
    +
    x_range_plot[1]
) / 2


benchmark_cy = (
    y_range_plot[0]
    +
    y_range_plot[1]
) / 2


fig.add_shape(
    type="rect",
    x0=x_range_plot[0],
    x1=x_range_plot[1],
    y0=y_range_plot[0],
    y1=y_range_plot[1],
    fillcolor=benchmark_color[
        "fill"
    ],
    line=dict(
        color=benchmark_color[
            "line"
        ],
        width=2.0,
        dash="dot"
    )
)


fig.add_annotation(
    x=benchmark_cx,
    y=benchmark_cy,
    xanchor="center",
    yanchor="middle",
    align="center",
    text=(
        f"<b>{benchmark_label}</b>"
    ),
    showarrow=False,
    font=dict(
        size=10.5,
        color="#1F2937"
    ),
    bgcolor=(
        "rgba(255,255,255,0.84)"
    ),
    bordercolor=benchmark_color[
        "line"
    ],
    borderwidth=0.8,
    borderpad=2.0
)


inside_benchmark = (

    x_range_plot[0]
    <=
    x_plot
    <=
    x_range_plot[1]

    and

    y_range_plot[0]
    <=
    y_plot
    <=
    y_range_plot[1]
)


if not inside_benchmark:

    fig.add_shape(
        type="line",
        x0=benchmark_cx,
        y0=benchmark_cy,
        x1=x_plot,
        y1=y_plot,
        line=dict(
            color=benchmark_color[
                "line"
            ],
            width=1.4,
            dash="dot"
        ),
        layer="below"
    )


    gap_x = (
        benchmark_cx
        +
        (
            x_plot
            -
            benchmark_cx
        )
        *
        0.52
    )


    gap_y = (
        benchmark_cy
        +
        (
            y_plot
            -
            benchmark_cy
        )
        *
        0.52
    )


    fig.add_annotation(
        x=gap_x,
        y=gap_y,
        text="<b>Gap</b>",
        showarrow=False,
        font=dict(
            size=9.2,
            color="#2F343B"
        ),
        bgcolor=(
            "rgba(255,255,255,0.82)"
        ),
        borderpad=1.5
    )


pin_text_y = max(
    0.35,
    y_plot - 0.62
)


fig.add_trace(

    go.Scatter(

        x=[
            x_plot
        ],

        y=[
            y_plot
        ],

        mode="text",

        text=[
            "📍"
        ],

        textfont=dict(
            size=21,
            color="#C53030"
        ),

        hovertemplate=(
            f"Market Reach: "
            f"{x_score:.1f}"
            f"<br>"
            f"Operational Maturity: "
            f"{y_score:.1f}"
            f"<extra></extra>"
        ),

        showlegend=False
    )
)


fig.add_annotation(
    x=x_plot,
    y=pin_text_y,
    text=(
        "<b>Your position</b>"
    ),
    showarrow=False,
    font=dict(
        size=12,
        color="#C53030"
    )
)


def add_stage_label(
    x,
    y,
    stage_name,
    descriptor,
    xanchor
):

    fig.add_annotation(
        x=x,
        y=y,
        text=(
            f"<b>{stage_name}</b>"
            f"<br>"
            f"<span style='font-size:10px'>"
            f"{descriptor}"
            f"</span>"
        ),
        showarrow=False,
        xanchor=xanchor,
        yanchor="top",
        align="left",
        font=dict(
            size=13,
            color="#475569"
        )
    )


add_stage_label(
    0.55,
    9.55,
    "Growing",
    "Ready for more customers",
    "left"
)


add_stage_label(
    9.45,
    9.55,
    "Established",
    "In balance",
    "right"
)


add_stage_label(
    0.55,
    4.55,
    "Starting",
    "Building the base",
    "left"
)


add_stage_label(
    9.45,
    4.55,
    "Fixing",
    "Growing pains",
    "right"
)


fig.add_annotation(
    x=0.5,
    y=-0.14,
    xref="paper",
    yref="paper",
    text=(
        "<b>Market reach</b>"
        "<br>"
        "<span style='font-size:10px'>"
        "(more ways customers can find and buy from you)"
        "</span>"
    ),
    showarrow=False,
    align="center",
    font=dict(
        size=11.0,
        color="#64748B"
    )
)


fig.add_annotation(
    x=-0.070,
    y=0.5,
    xref="paper",
    yref="paper",
    text=(
        "<b>Operational maturity</b>"
        "<br>"
        "<span style='font-size:10px'>"
        "(more repeatable systems)"
        "</span>"
    ),
    showarrow=False,
    textangle=-90,
    align="center",
    font=dict(
        size=11.5,
        color="#64748B"
    )
)


fig.update_layout(

    height=390,

    margin=dict(
        l=78,
        r=12,
        t=12,
        b=62
    ),

    paper_bgcolor="white",

    plot_bgcolor="#FCFCFB",

    xaxis=dict(
        range=[
            0,
            10.25
        ],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title="",
        fixedrange=True
    ),

    yaxis=dict(
        range=[
            0,
            10.25
        ],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title="",
        fixedrange=True
    ),

    hoverlabel=dict(
        bgcolor="white",
        font_size=12
    )
)


# =========================================================
# CREATE DOWNLOADABLE PNG
# =========================================================
result_png_bytes = None
export_error = None


try:

    result_png_bytes = build_result_png(

        fig=fig,

        stage=stage,

        map_stage=map_stage,

        business_type=business_type,

        concern=concern,

        find_answers=find_answers,

        buy_answers=buy_answers,

        systems_answer=systems_answer,

        conclusion_html=conclusion,

        disclaimer_text=disclaimer
    )


except Exception as error:

    export_error = error


# =========================================================
# TITLE + SMALL SAVE BUTTON
# =========================================================
#
# Button column is deliberately wider than before so the
# text remains on ONE LINE.
#
# Blank third column keeps the button beside the title
# rather than on the far-right side of the page.
#
title_col, save_col, title_space = st.columns(
    [
        3.80,
        1.45,
        4.75
    ],
    gap="small"
)


with title_col:

    st.markdown(
        (
            '<div class="hero-title">'
            'Your Business Stage Map'
            '</div>'
        ),
        unsafe_allow_html=True
    )


with save_col:

    if result_png_bytes is not None:

        st.download_button(
            label="↓  Save my result",
            data=result_png_bytes,
            file_name="my-business-stage-map.png",
            mime="image/png",
            type="secondary",
            use_container_width=False,
            key="save_result_top"
        )


# =========================================================
# HEADER DETAILS
# =========================================================
st.markdown(
    (
        f"<div class='meta'>"

        f"<span class='meta-line'>"
        f"<b>You think you're at:</b> "
        f"{stage}"
        f"</span>"

        f"<span class='meta-line'>"
        f"<b>Your answers show:</b> "
        f"{map_stage}"
        f"</span>"

        f"</div>"
    ),
    unsafe_allow_html=True
)


st.markdown(
    (
        f'<span class="pill">'
        f'{business_type}'
        f'</span>'

        f'<span class="pill">'
        f'Concern: {concern}'
        f'</span>'
    ),
    unsafe_allow_html=True
)


if export_error is not None:

    st.caption(
        (
            "Your result is displayed correctly, "
            "but the PNG download is temporarily unavailable."
        )
    )


# =========================================================
# MAP + INTERPRETATION
# =========================================================
left, right = st.columns(
    [
        2.35,
        1.0
    ],
    gap="large"
)


with left:

    st.markdown(
        (
            '<div class="map-logic">'

            '<b>How this map works:</b> '

            'Your position is based on how customers find '
            'and buy from you (questions 5–6) and how '
            'repeatable your systems are (question 7). '

            'The benchmark is based on the stage you '
            'selected (question 3).'

            '</div>'
        ),
        unsafe_allow_html=True
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )


    st.markdown(
        f"""
<div class="disclaimer-under-chart">
{disclaimer}
</div>
""",
        unsafe_allow_html=True
    )


with right:

    dashboard_html = f"""
<div class="summary-card">

<div class="summary-kicker">
Your answers at a glance
</div>

<div class="dash-item">

<div class="dash-label">
How customers find you
</div>

<div class="dash-value">
{find_display}
</div>

</div>

<div class="dash-item">

<div class="dash-label">
How customers buy
</div>

<div class="dash-value">
{buy_display}
</div>

</div>

<div class="dash-item">

<div class="dash-label">
Repeatable systems
</div>

<div class="systems-value">
{systems_display}
</div>

</div>

<div class="result-wrap">

<div class="result-label">
What this suggests
</div>

<p class="result-line">
{conclusion}
</p>

</div>

</div>
"""


    st.markdown(
        dashboard_html,
        unsafe_allow_html=True
    )

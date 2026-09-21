"""
Tema visual institucional del Asistente Académico Inteligente.

Diseño inspirado en una aplicación universitaria:
- naranja como color de énfasis;
- negro y gris oscuro para identidad institucional;
- fondo claro;
- tarjetas limpias;
- navegación sobria;
- componentes reutilizables.
"""

import html

import streamlit as st

import db


# ============================================================
# PALETA
# ============================================================

UNFV_ORANGE = "#F28C28"
UNFV_ORANGE_DARK = "#D97706"
UNFV_ORANGE_SOFT = "#FFF3E6"

DARK = "#202124"
TEXT = "#28313F"
TEXT_SOFT = "#667085"

BACKGROUND = "#F6F7F9"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F1F3F5"
BORDER = "#E3E6EA"

SUCCESS = "#2E7D5B"
WARNING = "#B7791F"
ERROR = "#B5473C"
INFO = "#3E5C8A"


COLORS = {

    db.STATUS_NUEVO: {
        "ink": "#667085",
        "soft": "#F2F4F7",
        "label": "Nuevo",
    },

    db.STATUS_DEBIL: {
        "ink": "#B7791F",
        "soft": "#FFF4DD",
        "label": "Requiere refuerzo",
    },

    db.STATUS_REFORZADO: {
        "ink": "#3E5C8A",
        "soft": "#EDF2FA",
        "label": "En refuerzo",
    },

    db.STATUS_DOMINADO: {
        "ink": "#2E7D5B",
        "soft": "#EAF5F0",
        "label": "Dominado",
    },
}


PRIMARY = UNFV_ORANGE
CORRECT = SUCCESS
INCORRECT = ERROR


def status_colors(status):
    return COLORS.get(status, COLORS[db.STATUS_NUEVO])


# ============================================================
# CSS GLOBAL
# ============================================================

def inject_css():

    st.markdown(
        f"""
        <style>

        /* ===================================================
           VARIABLES
        =================================================== */

        :root {{

            --unfv-orange: {UNFV_ORANGE};
            --unfv-orange-dark: {UNFV_ORANGE_DARK};
            --unfv-orange-soft: {UNFV_ORANGE_SOFT};

            --background: {BACKGROUND};
            --surface: {SURFACE};
            --surface-alt: {SURFACE_ALT};

            --dark: {DARK};
            --text: {TEXT};
            --text-soft: {TEXT_SOFT};

            --border: {BORDER};

        }}


        /* ===================================================
           GENERAL
        =================================================== */

        html,
        body,
        [class*="css"] {{
            font-family:
                Inter,
                "Segoe UI",
                Arial,
                sans-serif;
        }}


        .stApp {{
            background-color: var(--background);
        }}


        [data-testid="stAppViewContainer"] {{
            color: var(--text);
        }}


        .block-container {{

            max-width: 1280px;

            padding-top: 2rem;

            padding-bottom: 4rem;

        }}


        h1,
        h2,
        h3,
        h4 {{

            font-family:
                Inter,
                "Segoe UI",
                Arial,
                sans-serif !important;

            color: var(--dark);

            font-weight: 700 !important;

        }}


        p {{
            color: var(--text);
        }}


        /* ===================================================
           SIDEBAR
        =================================================== */

        section[data-testid="stSidebar"] {{

            background-color: #FFFFFF;

            border-right: 1px solid var(--border);

        }}


        section[data-testid="stSidebar"] .block-container {{

            padding-top: 1.4rem;

        }}


        .unfv-sidebar-brand {{

            padding:
                0.5rem
                0.35rem
                1.2rem
                0.35rem;

        }}


        .unfv-sidebar-university {{

            color: var(--unfv-orange);

            font-size: 0.70rem;

            font-weight: 800;

            letter-spacing: 0.08em;

            margin-bottom: 0.45rem;

        }}


        .unfv-sidebar-title {{

            font-size: 1.15rem;

            font-weight: 750;

            line-height: 1.2;

            color: var(--dark);

            margin-bottom: 0.3rem;

        }}


        .unfv-sidebar-subtitle {{

            color: var(--text-soft);

            font-size: 0.78rem;

            line-height: 1.4;

        }}


        .unfv-sidebar-footer {{

            margin-top: 1.4rem;

            padding-top: 1rem;

            border-top: 1px solid var(--border);

            font-size: 0.72rem;

            line-height: 1.5;

            color: var(--text-soft);

        }}


        /* ===================================================
           NAVEGACIÓN
        =================================================== */

        [data-testid="stNavSectionHeader"] {{

            font-size: 0.68rem;

            text-transform: uppercase;

            letter-spacing: 0.08em;

            color: var(--text-soft);

            font-weight: 700;

            margin-top: 0.7rem;

        }}


        section[data-testid="stSidebar"]
        a[data-testid*="NavLink"] {{

            border-radius: 8px;

            margin:
                0.10rem
                0;

            font-weight: 500;

        }}


        section[data-testid="stSidebar"]
        a[aria-current="page"] {{

            background-color:
                var(--unfv-orange-soft) !important;

            color:
                var(--unfv-orange-dark) !important;

            font-weight:
                650 !important;

        }}


        /* ===================================================
           HEADER
        =================================================== */

        .unfv-header {{

            background:
                var(--surface);

            border:
                1px solid
                var(--border);

            border-left:
                5px solid
                var(--unfv-orange);

            border-radius:
                12px;

            padding:
                1.5rem
                1.7rem;

            margin-bottom:
                1.6rem;

            box-shadow:
                0 3px 14px
                rgba(20, 25, 35, 0.04);

        }}


        .unfv-header-label {{

            color:
                var(--unfv-orange-dark);

            font-size:
                0.72rem;

            font-weight:
                800;

            letter-spacing:
                0.08em;

            text-transform:
                uppercase;

            margin-bottom:
                0.5rem;

        }}


        .unfv-header-title {{

            color:
                var(--dark);

            font-size:
                2rem;

            font-weight:
                750;

            line-height:
                1.15;

            margin:
                0 0
                0.45rem
                0;

        }}


        .unfv-header-subtitle {{

            color:
                var(--text-soft);

            font-size:
                0.96rem;

            line-height:
                1.55;

            max-width:
                760px;

            margin:
                0;

        }}


        /* ===================================================
           BOTONES
        =================================================== */

        .stButton > button,
        .stFormSubmitButton > button {{

            border-radius:
                8px;

            min-height:
                42px;

            font-weight:
                600;

            border:
                1px solid
                var(--border);

            transition:
                all
                0.15s
                ease-in-out;

        }}


        .stButton > button:hover,
        .stFormSubmitButton > button:hover {{

            border-color:
                var(--unfv-orange);

            color:
                var(--unfv-orange-dark);

        }}


        [data-testid="stBaseButton-primary"] {{

            background-color:
                var(--unfv-orange) !important;

            border-color:
                var(--unfv-orange) !important;

            color:
                white !important;

        }}


        [data-testid="stBaseButton-primary"]:hover {{

            background-color:
                var(--unfv-orange-dark) !important;

            border-color:
                var(--unfv-orange-dark) !important;

            color:
                white !important;

        }}


        /* ===================================================
           INPUTS
        =================================================== */

        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div {{

            border-radius:
                8px !important;

        }}


        .stTextInput input,
        .stTextArea textarea {{

            border-radius:
                8px !important;

        }}


        /* ===================================================
           FILE UPLOADER
        =================================================== */

        [data-testid="stFileUploader"] {{

            background:
                var(--surface);

            border-radius:
                10px;

        }}


        /* ===================================================
           CHAT
        =================================================== */

        [data-testid="stChatMessage"] {{

            background:
                #FFFFFF;

            border:
                1px solid
                var(--border);

            border-radius:
                12px;

            margin-bottom:
                0.8rem;

            box-shadow:
                0 2px 8px
                rgba(20, 25, 35, 0.035);

        }}


        [data-testid="stChatMessage"]
        [data-testid="stChatMessageAvatarAssistant"] {{

            background:
                var(--unfv-orange-soft);

        }}


        [data-testid="stChatMessage"]:has(
            [data-testid="stChatMessageAvatarAssistant"]
        ) {{

            border-left:
                4px solid
                var(--unfv-orange);

        }}


        [data-testid="stChatMessage"]:has(
            [data-testid="stChatMessageAvatarUser"]
        ) {{

            border-left:
                4px solid
                #79808B;

        }}


        /* ===================================================
           TARJETAS ESTADÍSTICAS
        =================================================== */

        .stat-row {{

            display:
                grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(155px, 1fr)
                );

            gap:
                1rem;

            margin-bottom:
                1.5rem;

        }}


        .stat-tile {{

            background:
                var(--surface);

            border:
                1px solid
                var(--border);

            border-top:
                4px solid
                var(
                    --color-tone,
                    var(--unfv-orange)
                );

            border-radius:
                10px;

            padding:
                1rem 1.1rem;

            box-shadow:
                0 3px 12px
                rgba(20, 25, 35, 0.035);

        }}


        .stat-value {{

            font-size:
                1.7rem;

            font-weight:
                750;

            color:
                var(--dark);

        }}


        .stat-label {{

            font-size:
                0.78rem;

            color:
                var(--text-soft);

            margin-top:
                0.35rem;

        }}


        /* ===================================================
           TEMAS
        =================================================== */

        .topic-grid {{

            display:
                grid;

            grid-template-columns:
                repeat(
                    auto-fill,
                    minmax(245px, 1fr)
                );

            gap:
                1rem;

            margin-top:
                0.7rem;

        }}


        .topic-card {{

            background:
                var(--surface);

            border:
                1px solid
                var(--border);

            border-left:
                4px solid
                var(
                    --color-tone,
                    var(--unfv-orange)
                );

            border-radius:
                10px;

            padding:
                1rem;

            box-shadow:
                0 2px 10px
                rgba(20, 25, 35, 0.03);

        }}


        .topic-card-top {{

            display:
                flex;

            justify-content:
                space-between;

            align-items:
                flex-start;

            gap:
                0.5rem;

            margin-bottom:
                0.35rem;

        }}


        .topic-name {{

            color:
                var(--dark);

            font-weight:
                650;

            font-size:
                0.98rem;

        }}


        .topic-meta {{

            color:
                var(--text-soft);

            font-size:
                0.78rem;

            margin-bottom:
                0.55rem;

        }}


        .mastery-track {{

            height:
                7px;

            background:
                var(--surface-alt);

            border-radius:
                10px;

            overflow:
                hidden;

        }}


        .mastery-fill {{

            height:
                100%;

            background:
                var(
                    --color-tone,
                    var(--unfv-orange)
                );

            border-radius:
                10px;

        }}


        /* ===================================================
           BADGES
        =================================================== */

        .badge {{

            display:
                inline-block;

            font-size:
                0.75rem;

            font-weight:
                600;

            padding:
                0.20rem
                0.55rem;

            border-radius:
                20px;

            white-space:
                nowrap;

        }}


        .pdf-chip {{

            display:
                inline-block;

            font-size:
                0.78rem;

            color:
                var(--text);

            background:
                var(--surface-alt);

            border:
                1px solid
                var(--border);

            border-radius:
                20px;

            padding:
                0.28rem
                0.7rem;

            margin:
                0
                0.35rem
                0.35rem
                0;

        }}


        /* ===================================================
           BARRAS
        =================================================== */

        .bar-row {{

            display:
                grid;

            grid-template-columns:
                minmax(130px, 12rem)
                1fr
                3rem;

            align-items:
                center;

            gap:
                0.75rem;

            margin-bottom:
                0.55rem;

        }}


        .bar-label {{

            font-size:
                0.84rem;

            color:
                var(--text);

            overflow:
                hidden;

            text-overflow:
                ellipsis;

            white-space:
                nowrap;

        }}


        .bar-track {{

            height:
                9px;

            background:
                var(--surface-alt);

            border-radius:
                10px;

            overflow:
                hidden;

        }}


        .bar-fill {{

            height:
                100%;

            border-radius:
                10px;

            background:
                var(
                    --color-tone,
                    var(--unfv-orange)
                );

        }}


        .bar-value {{

            font-size:
                0.78rem;

            color:
                var(--text-soft);

            text-align:
                right;

        }}


        /* ===================================================
           QUIZ
        =================================================== */

        [data-testid="stForm"] {{

            background:
                var(--surface);

            border:
                1px solid
                var(--border);

            border-left:
                4px solid
                var(--unfv-orange);

            border-radius:
                10px;

            padding:
                1.3rem
                1.4rem;

            box-shadow:
                0 2px 9px
                rgba(20, 25, 35, 0.03);

        }}


        /* ===================================================
           EXPANDERS
        =================================================== */

        [data-testid="stExpander"] {{

            background:
                var(--surface);

            border:
                1px solid
                var(--border);

            border-radius:
                9px;

        }}


        /* ===================================================
           ESTADOS VACÍOS
        =================================================== */

        .empty-state {{

            background:
                var(--surface);

            border:
                1px dashed
                #C9CED6;

            border-radius:
                12px;

            padding:
                2.6rem
                1.5rem;

            text-align:
                center;

            margin-top:
                0.7rem;

        }}


        .empty-state-title {{

            color:
                var(--dark);

            font-size:
                1.1rem;

            font-weight:
                700;

            margin-bottom:
                0.4rem;

        }}


        .empty-state-body {{

            color:
                var(--text-soft);

            font-size:
                0.9rem;

            max-width:
                520px;

            margin:
                auto;

        }}


        /* ===================================================
           ALERTAS / FEEDBACK
        =================================================== */

        .feedback-banner {{

            border-left:
                4px solid
                var(
                    --color-tone,
                    var(--unfv-orange)
                );

            background:
                var(--surface-alt);

            border-radius:
                8px;

            padding:
                0.75rem
                1rem;

            font-size:
                0.87rem;

            color:
                var(--text);

            margin-top:
                0.6rem;

        }}


        .weak-topic-line {{

            padding:
                0.5rem
                0.8rem;

            border-left:
                3px solid
                {WARNING};

            background:
                #FFF9ED;

            border-radius:
                0 7px 7px 0;

            margin-bottom:
                0.4rem;

            font-size:
                0.88rem;

        }}


        /* ===================================================
           STREAMLIT UI
        =================================================== */

        footer {{
            visibility: hidden;
        }}


        #MainMenu {{
            visibility: hidden;
        }}


        hr {{

            border-color:
                var(--border) !important;

        }}


        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ENCABEZADO DE PÁGINA
# ============================================================

def render_header(title, subtitle):
    header_html = (
        '<div class="unfv-header">'
        '<div class="unfv-header-label">'
        'UNIVERSIDAD NACIONAL FEDERICO VILLARREAL'
        '</div>'
        f'<div class="unfv-header-title">{html.escape(title)}</div>'
        f'<div class="unfv-header-subtitle">{html.escape(subtitle)}</div>'
        '</div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True
    )


# ============================================================
# MARCA DEL SIDEBAR
# ============================================================

def render_sidebar_brand():
    sidebar_html = (
        '<div class="unfv-sidebar-brand">'
        '<div class="unfv-sidebar-university">UNFV</div>'
        '<div class="unfv-sidebar-title">'
        'Asistente Académico Inteligente'
        '</div>'
        '<div class="unfv-sidebar-subtitle">'
        'Universidad Nacional Federico Villarreal'
        '<br>'
        'Ingeniería de Sistemas'
        '</div>'
        '</div>'
    )

    st.sidebar.markdown(
        sidebar_html,
        unsafe_allow_html=True
    )


# ============================================================
# ESTADO DE SESIÓN EN SIDEBAR
# ============================================================

def render_sidebar_status():

    if st.session_state.get("docs_ready"):
        pdf_names = st.session_state.get("pdf_names", [])
        status_text = f"{len(pdf_names)} documento(s) procesado(s)"
        status_icon = "●"
    else:
        status_text = "Sin documentos procesados"
        status_icon = "○"

    sidebar_status_html = (
        '<div class="unfv-sidebar-footer">'
        '<div style="font-weight:700; color:#202124; margin-bottom:6px;">'
        'Sesión académica'
        '</div>'
        '<div style="font-size:12px; color:#667085; margin-bottom:16px;">'
        f'{status_icon} {html.escape(status_text)}'
        '</div>'
        '<div style="font-size:11px; line-height:1.6; color:#8A9099;">'
        'Facultad de Ingeniería Industrial y de Sistemas'
        '<br>'
        'Escuela Profesional de Ingeniería de Sistemas'
        '</div>'
        '</div>'
    )

    st.sidebar.markdown(
        sidebar_status_html,
        unsafe_allow_html=True
    )


# ============================================================
# BADGES
# ============================================================

def status_badge_html(status):

    cfg = status_colors(status)

    return (
        f'<span class="badge" '
        f'style="background:{cfg["soft"]};'
        f'color:{cfg["ink"]};">'
        f'{html.escape(cfg["label"])}'
        f"</span>"
    )


def tag_badge_html(text):

    return (
        '<span class="badge" '
        'style="background:#FFF3E6;'
        'color:#C96A00;">'
        f'{html.escape(str(text))}'
        "</span>"
    )


# ============================================================
# CHIPS DE PDF
# ============================================================

def pdf_chips_html(pdf_names):

    if not pdf_names:
        return ""

    return "".join(
        f'<span class="pdf-chip">📄 {html.escape(name)}</span>'
        for name in pdf_names
    )


# ============================================================
# TARJETAS DE ESTADÍSTICAS
# ============================================================

def render_stat_row(items):
    """Muestra tarjetas con estadísticas resumidas."""

    cards = []

    for label, value, color in items:

        tone = color or UNFV_ORANGE

        card_html = (
            f'<div class="stat-tile" style="--color-tone:{tone};">'
            f'<div class="stat-value">{html.escape(str(value))}</div>'
            f'<div class="stat-label">{html.escape(str(label))}</div>'
            '</div>'
        )

        cards.append(card_html)

    stats_html = (
        '<div class="stat-row">'
        + "".join(cards)
        + '</div>'
    )

    st.markdown(
        stats_html,
        unsafe_allow_html=True
    )

# ============================================================
# GRID DE TEMAS
# ============================================================

def render_topic_grid(topics):
    """Muestra los temas académicos en tarjetas."""

    cards = []

    for topic in topics:

        cfg = status_colors(
            topic["status"]
        )

        score = int(
            topic.get(
                "mastery_score",
                0
            )
            or 0
        )

        name = html.escape(
            str(topic["name"])
        )

        query_count = topic["query_count"]

        badge = status_badge_html(
            topic["status"]
        )

        card_html = (
            f'<div class="topic-card" style="--color-tone:{cfg["ink"]};">'
            '<div class="topic-card-top">'
            f'<div class="topic-name">{name}</div>'
            f'{badge}'
            '</div>'
            '<div class="topic-meta">'
            f'{query_count} consulta(s) · Dominio: {score}%'
            '</div>'
            '<div class="mastery-track">'
            f'<div class="mastery-fill" '
            f'style="width:{score}%; --color-tone:{cfg["ink"]};">'
            '</div>'
            '</div>'
            '</div>'
        )

        cards.append(
            card_html
        )

    topics_html = (
        '<div class="topic-grid">'
        + "".join(cards)
        + '</div>'
    )

    st.markdown(
        topics_html,
        unsafe_allow_html=True
    )


# ============================================================
# BARRAS DE FRECUENCIA
# ============================================================

def render_frequency_bars(topics):
    """Muestra barras horizontales según la frecuencia de consultas."""

    if not topics:
        return

    max_count = max(
        topic["query_count"]
        for topic in topics
    )

    if max_count <= 0:
        max_count = 1

    rows = []

    for topic in topics:

        cfg = status_colors(
            topic["status"]
        )

        count = topic["query_count"]

        width = max(
            4,
            (count / max_count) * 100
        )

        name = html.escape(
            str(topic["name"])
        )

        row_html = (
            '<div class="bar-row">'
            f'<div class="bar-label">{name}</div>'
            '<div class="bar-track">'
            f'<div class="bar-fill" '
            f'style="width:{width}%; --color-tone:{cfg["ink"]};">'
            '</div>'
            '</div>'
            f'<div class="bar-value">{count}</div>'
            '</div>'
        )

        rows.append(
            row_html
        )

    st.markdown(
        "".join(rows),
        unsafe_allow_html=True
    )

# ============================================================
# TEMAS DÉBILES
# ============================================================

def weak_topic_line_html(topic):

    if isinstance(topic, dict):
        name = topic["name"]
    else:
        name = str(topic)

    return (
        '<div class="weak-topic-line">'
        f'{html.escape(name)}'
        "</div>"
    )


# ============================================================
# FEEDBACK DE QUIZ
# ============================================================

def feedback_banner_html(is_correct, explanation):

    tone = (
        CORRECT
        if is_correct
        else INCORRECT
    )

    title = (
        "Respuesta correcta"
        if is_correct
        else "Respuesta incorrecta"
    )

    return (
        f'<div class="feedback-banner" '
        f'style="--color-tone:{tone};">'
        f"<strong>{title}</strong><br>"
        f"{html.escape(explanation or '')}"
        "</div>"
    )


# ============================================================
# ESTADO VACÍO
# ============================================================

def render_empty_state(title, body):

    empty_html = (
        '<div class="empty-state">'
        f'<div class="empty-state-title">{html.escape(title)}</div>'
        f'<div class="empty-state-body">{html.escape(body)}</div>'
        '</div>'
    )

    st.markdown(
        empty_html,
        unsafe_allow_html=True
    )
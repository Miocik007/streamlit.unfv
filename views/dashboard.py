"""Página: Dashboard de progreso."""

import pandas as pd
import streamlit as st

import db
import theme

STATUS_FILTER_OPTIONS = {
    "Todos los estados": None,
    "🆕 Nuevo": db.STATUS_NUEVO,
    "⚠️ Punto débil": db.STATUS_DEBIL,
    "🔄 En refuerzo": db.STATUS_REFORZADO,
    "✅ Dominado": db.STATUS_DOMINADO,
}

SORT_OPTIONS = {
    "Más consultado primero": ("query_count", True),
    "Menor dominio primero": ("mastery_score", False),
    "Nombre (A-Z)": ("name", False),
}


def render():
    theme.render_header(
    "Progreso Académico",
    "Revisa tu nivel de dominio, frecuencia de consultas y los temas que requieren mayor refuerzo.",
)

    topics = db.get_all_topics()
    if not topics:
        theme.render_empty_state(
            "📊 Todavía no hay datos de progreso",
            "Haz algunas preguntas en el 💬 Chat para que empiecen a aparecer "
            "temas y estadísticas aquí.",
        )
        return

    _render_stats(topics)
    _render_trend_chart()

    st.markdown("##### Frecuencia de consultas por tema")
    theme.render_frequency_bars(topics)

    st.write("")
    st.markdown("##### Detalle por tema")
    _render_topic_grid(topics)


def _render_stats(topics):
    stats = db.get_stats_summary()
    n_debil = sum(1 for t in topics if t["status"] == db.STATUS_DEBIL)
    n_reforzado = sum(1 for t in topics if t["status"] == db.STATUS_REFORZADO)
    n_dominado = sum(1 for t in topics if t["status"] == db.STATUS_DOMINADO)

    theme.render_stat_row(
        [
            ("Temas totales", len(topics), None),
            ("Puntos débiles activos", n_debil, theme.COLORS[db.STATUS_DEBIL]["ink"]),
            ("En refuerzo", n_reforzado, theme.COLORS[db.STATUS_REFORZADO]["ink"]),
            ("Dominados", n_dominado, theme.COLORS[db.STATUS_DOMINADO]["ink"]),
            (
                "Precisión en quizzes",
                f"{stats['accuracy']}%" if stats["total_answered"] else "—",
                None,
            ),
        ]
    )


def _render_trend_chart():
    daily = db.get_daily_query_counts(days=14)
    if len(daily) < 2:
        return
    st.markdown("##### Preguntas por día (últimos días con actividad)")
    df = pd.DataFrame(daily, columns=["Día", "Preguntas"]).set_index("Día")
    st.bar_chart(df, color=theme.PRIMARY, use_container_width=True)
    st.write("")


def _render_topic_grid(topics):
    filt_col, sort_col = st.columns(2)
    with filt_col:
        status_label = st.selectbox("Filtrar por estado", list(STATUS_FILTER_OPTIONS.keys()))
    with sort_col:
        sort_label = st.selectbox("Ordenar por", list(SORT_OPTIONS.keys()))

    status_value = STATUS_FILTER_OPTIONS[status_label]
    filtered = [t for t in topics if status_value is None or t["status"] == status_value]

    sort_key, reverse = SORT_OPTIONS[sort_label]
    filtered = sorted(filtered, key=lambda t: t[sort_key], reverse=reverse)

    if not filtered:
        st.caption("Ningún tema coincide con este filtro.")
        return
    theme.render_topic_grid(filtered)

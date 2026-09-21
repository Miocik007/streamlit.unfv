"""
Asistente Académico Inteligente - UNFV

Sistema de estudio adaptativo basado en documentos PDF, RAG e Inteligencia Artificial.
"""

import asyncio

import streamlit as st

import db
import state
import theme

from views import chat, dashboard, history, quiz, settings


try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


def main():

    st.set_page_config(
        page_title="Asistente Académico Inteligente | UNFV",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Aplicar diseño institucional
    theme.inject_css()

    # Inicializar base de datos
    db.init_db()

    # Inicializar variables de sesión
    state.init_session_state()

    # Identidad de la aplicación
    theme.render_sidebar_brand()

    # Estado de la sesión
    theme.render_sidebar_status()

    # Navegación principal
    pages = {

        "Asistente Académico": [

            st.Page(
                chat.render,
                title="Asistente",
                icon="💬",
                url_path="asistente",
                default=True,
            ),

            st.Page(
                dashboard.render,
                title="Progreso",
                icon="📊",
                url_path="progreso",
            ),

            st.Page(
                quiz.render,
                title="Evaluación",
                icon="📝",
                url_path="evaluacion",
            ),

            st.Page(
                history.render,
                title="Historial",
                icon="🕘",
                url_path="historial",
            ),
        ],

        "Sistema": [

            st.Page(
                settings.render,
                title="Documentos y configuración",
                icon="⚙️",
                url_path="configuracion",
            ),
        ],
    }

    pg = st.navigation(pages)

    pg.run()


if __name__ == "__main__":
    main()
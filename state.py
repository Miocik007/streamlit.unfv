"""
Estado compartido entre páginas.

Con una app multipágina cada página es una función independiente, así que
en vez de pasar un diccionario de configuración de página en página, los
valores de configuración (API key, modelo, umbrales) viven directamente en
``st.session_state`` y cada página los lee o escribe según lo necesite.
"""

import streamlit as st

import rag_engine as rag

DEFAULT_MODEL = "gemini-3.8-flash"


def init_session_state():
    defaults = {
        # Documentos / RAG
        "vector_store": None,
        "full_text": "",
        "docs_ready": False,
        "pdf_names": [],
        # Chat (solo de la sesión actual; el historial persistente vive en la BD)
        "chat_messages": [],
        "quiz_feedback": {},
        # Parámetros de aprendizaje adaptativo
        "threshold": 3,
        "questions_per_topic": 3,
        "max_topics_per_quiz": 3,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_current_llm():
    """Crea el modelo Gemini utilizando la configuración privada del sistema."""

    api_key = st.secrets["GOOGLE_API_KEY"]

    model_name = st.secrets.get(
        "GEMINI_MODEL",
        DEFAULT_MODEL
    )

    return rag.get_llm(
        api_key,
        model_name
    )
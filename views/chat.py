"""Página: Chat con los documentos."""

import streamlit as st

import db
import rag_engine as rag
import state
import theme


def render():
    theme.render_header(
    "Asistente Académico",
    "Consulta tus documentos en lenguaje natural y recibe respuestas contextualizadas mediante Inteligencia Artificial.",
)

    if not st.session_state.docs_ready:
        theme.render_empty_state(
    "Todavía no hay documentos cargados",
    "Ve a Documentos y configuración en el menú lateral para subir tus PDFs y activar el asistente."
)
        return

    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown(theme.pdf_chips_html(st.session_state.pdf_names), unsafe_allow_html=True)
    with top_r:
        if st.session_state.chat_messages and st.button("🗑️ Limpiar chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    st.write("")

    for msg in st.session_state.chat_messages:
        with st.chat_message("user"):
            st.markdown(msg["question"])
        with st.chat_message("assistant"):
            st.markdown(msg["answer"])
            st.markdown(theme.tag_badge_html(f"Tema: {msg['topic']}"), unsafe_allow_html=True)
            _render_sources(msg.get("sources"))

    question = st.chat_input("Haz una pregunta sobre el contenido de tus PDFs")

    if question:
        llm = state.get_current_llm()
        if llm is None:
            st.warning("Configura tu Google API Key en ⚙️ Configuración antes de preguntar.")
            return

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Buscando en tus documentos..."):
                answer, sources = rag.answer_question(
                    llm, st.session_state.vector_store, question, return_sources=True
                )
                topics_list = db.get_all_topic_names()
                topic = rag.classify_topic(llm, question, topics_list)
                db.ensure_topics([topic])
                count, status, became_weak = db.log_question(
                    question,
                    answer,
                    topic,
                    ", ".join(st.session_state.pdf_names),
                    st.session_state.threshold,
                )
            st.markdown(answer)
            st.markdown(theme.tag_badge_html(f"Tema: {topic}"), unsafe_allow_html=True)
            _render_sources(sources)

        st.session_state.chat_messages.append(
            {"question": question, "answer": answer, "topic": topic, "sources": sources}
        )

        if became_weak:
            st.warning(
                f"El tema **{topic}** ya suma {count} consultas y fue marcado como "
                f"**punto débil**. Se priorizará en 🧠 Quiz adaptativo."
            )
            st.rerun()


def _render_sources(sources):
    """Muestra los fragmentos del PDF que el modelo usó para responder,
    para que el usuario pueda verificar la respuesta contra su propio material."""
    if not sources:
        return
    with st.expander(f"Ver {len(sources)} fragmento(s) del documento usados en esta respuesta"):
        for i, snippet in enumerate(sources, start=1):
            st.markdown(f"**Fragmento {i}**")
            trimmed = snippet.strip()
            st.caption(trimmed[:500] + ("…" if len(trimmed) > 500 else ""))

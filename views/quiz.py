"""Página: Quiz adaptativo."""

import streamlit as st

import db
import rag_engine as rag
import state
import theme


def render():
    theme.render_header(
    "Evaluación Adaptativa",
    "Refuerza los temas que requieren mayor atención mediante preguntas generadas a partir de tus documentos.",
)

    if not st.session_state.docs_ready:
        theme.render_empty_state(
            "🧠 Aún no puedes generar quizzes",
            "Procesa tus documentos primero en **⚙️ Configuración**.",
        )
        return

    weak_topics = db.get_weak_topics(limit=st.session_state.max_topics_per_quiz)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        if weak_topics:
            st.markdown("**Puntos débiles detectados actualmente**")
            st.markdown(
                "".join(theme.weak_topic_line_html(t) for t in weak_topics),
                unsafe_allow_html=True,
            )
        else:
            st.info(
                "Aún no hay puntos débiles. Sigue usando el 💬 Chat: cuando repitas "
                "preguntas sobre un mismo tema, aparecerá aquí."
            )

    with col_b:
        generate_clicked = st.button(
            "Generar quiz de puntos débiles",
            type="primary",
            use_container_width=True,
            disabled=not weak_topics,
        )

    if generate_clicked:
        llm = state.get_current_llm()
        if llm is None:
            st.warning("Configura tu Google API Key en ⚙️ Configuración.")
        else:
            created_any = False
            for t in weak_topics:
                if db.has_pending_quiz_for_topic(t["name"]):
                    continue
                with st.spinner(f"Generando preguntas para '{t['name']}'..."):
                    questions = rag.generate_quiz(
                        llm,
                        st.session_state.vector_store,
                        t["name"],
                        st.session_state.questions_per_topic,
                    )
                if questions:
                    db.save_quiz_questions(t["name"], questions)
                    created_any = True
            if created_any:
                st.success("Quiz generado a partir de tus puntos débiles.")
                st.rerun()
            else:
                st.info(
                    "Ya tenías preguntas pendientes para estos temas, o el LLM no "
                    "devolvió preguntas válidas."
                )

    st.divider()

    pending = db.get_pending_quiz_questions()
    if not pending:
        st.caption(
            "No hay preguntas de quiz pendientes por responder. Genera un quiz "
            "arriba, o revisa tu 🕘 Historial para ver respuestas pasadas."
        )
    else:
        st.markdown(f"##### Preguntas pendientes ({len(pending)})")
        letters = ["A", "B", "C", "D", "E", "F"]
        for q in pending:
            with st.form(key=f"quiz_form_{q['id']}"):
                st.markdown(theme.tag_badge_html(q["topic"]), unsafe_allow_html=True)
                st.markdown(f"**{q['question']}**")
                selected = st.radio(
                    "Selecciona una respuesta:",
                    options=list(range(len(q["options"]))),
                    format_func=lambda i, opts=q["options"]: f"{letters[i]}) {opts[i]}",
                    key=f"radio_{q['id']}",
                    index=None,
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button("Responder")
                if submitted:
                    if selected is None:
                        st.warning("Selecciona una opción antes de responder.")
                    else:
                        is_correct = db.record_quiz_answer(q["id"], selected)
                        st.session_state.quiz_feedback[q["id"]] = (is_correct, q["explanation"])
                        st.rerun()
            st.write("")

    recent_answered = db.get_answered_quiz_questions(limit=5)
    if recent_answered:
        st.write("")
        st.markdown("##### Últimas respuestas")
        for q in recent_answered:
            icon = "✅" if q["is_correct"] else "❌"
            st.caption(f"{icon} [{q['topic']}] {q['question']}")
        st.caption("Consulta el detalle completo, con filtros y búsqueda, en 🕘 Historial.")

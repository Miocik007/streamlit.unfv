"""Página: Documentos y Configuración.

Permite gestionar el material académico utilizado por el asistente,
configurar los parámetros del aprendizaje adaptativo y administrar
los datos de progreso del usuario.

La configuración interna del modelo de IA y la API Key no se muestra
en la interfaz. Estos valores se gestionan mediante Streamlit Secrets.
"""

import streamlit as st

import db
import rag_engine as rag
import state
import theme


def render():
    """Renderiza la página de documentos y configuración."""

    theme.render_header(
        "Documentos y Configuración",
        "Gestiona el material académico utilizado por el asistente y configura los parámetros del sistema.",
    )

    # ============================================================
    # MATERIAL ACADÉMICO
    # ============================================================

    _render_documents_section()

    st.divider()

    # ============================================================
    # APRENDIZAJE ADAPTATIVO
    # ============================================================

    _render_learning_section()

    st.divider()

    # ============================================================
    # DATOS
    # ============================================================

    _render_data_section()


# ================================================================
# DOCUMENTOS
# ================================================================

def _render_documents_section():
    """Permite cargar, procesar y eliminar los documentos de la sesión."""

    st.markdown("### 📄 Material académico")

    # ------------------------------------------------------------
    # Estado actual de los documentos
    # ------------------------------------------------------------

    if st.session_state.docs_ready:

        st.markdown(
            theme.pdf_chips_html(
                st.session_state.pdf_names
            ),
            unsafe_allow_html=True,
        )

        n_topics = len(
            db.get_all_topic_names()
        )

        st.caption(
            f"{len(st.session_state.pdf_names)} documento(s) procesado(s) · "
            f"{len(st.session_state.full_text):,} caracteres extraídos · "
            f"{n_topics} tema(s) identificados."
        )

    else:

        st.caption(
            "Todavía no has procesado ningún documento."
        )

    # ------------------------------------------------------------
    # Carga de archivos
    # ------------------------------------------------------------

    pdf_docs = st.file_uploader(
        "Sube uno o varios archivos PDF",
        accept_multiple_files=True,
        type=["pdf"],
        key="pdf_uploader",
    )

    # ------------------------------------------------------------
    # Botones
    # ------------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        process_clicked = st.button(
            "Procesar documentos",
            type="primary",
            use_container_width=True,
        )

    with col2:

        clear_clicked = st.button(
            "Quitar documentos de esta sesión",
            use_container_width=True,
            disabled=not st.session_state.docs_ready,
        )

    # ------------------------------------------------------------
    # Quitar documentos
    # ------------------------------------------------------------

    if clear_clicked:

        st.session_state.vector_store = None
        st.session_state.full_text = ""
        st.session_state.docs_ready = False
        st.session_state.pdf_names = []

        st.success(
            "Documentos removidos de esta sesión. "
            "Tu progreso guardado no se ha borrado."
        )

        st.rerun()

    # ------------------------------------------------------------
    # Procesar documentos
    # ------------------------------------------------------------

    if process_clicked:

        if not pdf_docs:

            st.warning(
                "Sube al menos un archivo PDF antes de procesar."
            )

            return

        try:

            # La API Key y el modelo ya NO vienen de la interfaz.
            # state.get_current_llm() los obtiene desde st.secrets.
            llm = state.get_current_llm()

        except Exception as exc:

            st.error(
                "No se pudo inicializar el modelo de Inteligencia Artificial."
            )

            st.caption(
                f"Detalle técnico: {exc}"
            )

            return

        try:

            _process_documents(
                pdf_docs,
                llm,
            )

        except Exception as exc:

            st.error(
                "Ocurrió un error al procesar los documentos."
            )

            st.caption(
                f"Detalle técnico: {exc}"
            )


# ================================================================
# PROCESAMIENTO DE DOCUMENTOS
# ================================================================

def _process_documents(pdf_docs, llm):
    """Extrae texto, genera chunks, construye FAISS e identifica temas."""

    # ------------------------------------------------------------
    # Extraer texto
    # ------------------------------------------------------------

    with st.spinner(
        "Extrayendo texto de los documentos..."
    ):

        full_text = rag.get_pdf_text(
            pdf_docs
        )

    if not full_text.strip():

        st.error(
            "No se pudo extraer texto de los PDFs subidos."
        )

        st.info(
            "Verifica que los documentos contengan texto seleccionable "
            "y no estén compuestos únicamente por imágenes escaneadas."
        )

        return

    # ------------------------------------------------------------
    # Crear fragmentos
    # ------------------------------------------------------------

    with st.spinner(
        "Preparando el contenido para la búsqueda semántica..."
    ):

        chunks = rag.get_text_chunks(
            full_text
        )

    if not chunks:

        st.error(
            "No se pudieron generar fragmentos de texto a partir de los documentos."
        )

        return

    # ------------------------------------------------------------
    # Crear índice vectorial
    # ------------------------------------------------------------

    with st.spinner(
        "Construyendo el índice de búsqueda semántica..."
    ):

        vector_store = rag.build_vector_store(
            chunks
        )

    # ------------------------------------------------------------
    # Detectar temas
    # ------------------------------------------------------------

    with st.spinner(
        "Identificando los principales temas del material..."
    ):

        topics = rag.extract_topics(
            llm,
            full_text,
        )

    if topics:

        db.ensure_topics(
            topics
        )

    # ------------------------------------------------------------
    # Guardar sesión
    # ------------------------------------------------------------

    st.session_state.vector_store = vector_store
    st.session_state.full_text = full_text
    st.session_state.docs_ready = True

    st.session_state.pdf_names = [
        pdf.name
        for pdf in pdf_docs
    ]

    # También dejamos disponibles los temas de esta sesión.
    st.session_state.active_topics = topics or []

    # ------------------------------------------------------------
    # Mensaje final
    # ------------------------------------------------------------

    st.success(
        f"Documentos procesados correctamente. "
        f"Se identificaron {len(topics or [])} tema(s)."
    )

    st.rerun()


# ================================================================
# APRENDIZAJE ADAPTATIVO
# ================================================================

def _render_learning_section():
    """Configuración de las reglas del aprendizaje adaptativo."""

    st.markdown(
        "### 🎯 Parámetros de aprendizaje"
    )

    st.caption(
        "Estos parámetros permiten ajustar cómo el sistema identifica "
        "temas que requieren refuerzo y genera evaluaciones."
    )

    st.slider(
        "Consultas repetidas para detectar un tema que requiere refuerzo",
        min_value=2,
        max_value=10,
        key="threshold",
        help=(
            "Cuando un tema alcanza esta cantidad de consultas, "
            "el sistema puede marcarlo como un tema que requiere refuerzo."
        ),
    )

    st.slider(
        "Preguntas de evaluación por tema",
        min_value=2,
        max_value=6,
        key="questions_per_topic",
        help=(
            "Número de preguntas que se generarán para cada tema "
            "seleccionado en la evaluación."
        ),
    )

    st.slider(
        "Temas a incluir por evaluación",
        min_value=1,
        max_value=5,
        key="max_topics_per_quiz",
        help=(
            "Número máximo de temas que pueden incluirse "
            "en una misma evaluación adaptativa."
        ),
    )


# ================================================================
# DATOS
# ================================================================

def _render_data_section():
    """Muestra estadísticas y permite reiniciar el progreso guardado."""

    st.markdown(
        "### 🗂️ Gestión de datos"
    )

    stats = db.get_stats_summary()

    st.caption(
        f"{stats['total_questions']} consulta(s) realizadas · "
        f"{stats['total_answered']} evaluación(es) respondida(s) · "
        f"{stats['total_topics']} tema(s) registrado(s)."
    )

    st.warning(
        "Reiniciar el progreso eliminará el historial de preguntas, "
        "temas identificados y resultados de evaluaciones."
    )

    confirm = st.checkbox(
        "Confirmo que quiero borrar todo mi progreso."
    )

    if st.button(
        "Reiniciar progreso",
        disabled=not confirm,
    ):

        db.reset_all()

        st.session_state.chat_messages = []
        st.session_state.quiz_feedback = []

        # Si estos datos existen en la sesión también los limpiamos.
        st.session_state.vector_store = None
        st.session_state.full_text = ""
        st.session_state.docs_ready = False
        st.session_state.pdf_names = []
        st.session_state.active_topics = []

        st.success(
            "El progreso fue reiniciado correctamente."
        )

        st.rerun()
"""
Motor de RAG y generación de contenido con LLM para el sistema de estudio
adaptativo.

Responsabilidades:
- Extraer texto de los PDFs y construir el índice vectorial (FAISS).
- Responder preguntas del usuario usando el contenido de los documentos.
- Extraer una lista de temas/conceptos clave del material subido.
- Clasificar cada pregunta del usuario dentro de esos temas.
- Generar preguntas de quiz (opción múltiple) a partir del contenido de
  los documentos, enfocadas en los puntos débiles del usuario.
"""

import json
import re

import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate


# ---------------------------------------------------------------------------
# Carga de documentos y construcción del índice vectorial
# ---------------------------------------------------------------------------

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text


def get_text_chunks(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return text_splitter.split_text(text)


@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def build_vector_store(text_chunks):
    embeddings = get_embeddings()
    return FAISS.from_texts(text_chunks, embedding=embeddings)


def get_llm(api_key, model_name, temperature=0.3):
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key,
    )


def _invoke_text(chain, inputs):
    """Invoca una chain LLM y devuelve el texto plano de la respuesta,
    soportando tanto respuestas string como bloques de contenido."""
    response = chain.invoke(inputs)
    content = response.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def _safe_json_extract(raw_text):
    """Intenta parsear JSON de la respuesta de un LLM, tolerando
    fences de markdown (```json ... ```) y texto extra alrededor."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned.strip(), flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned.strip()).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Fallback: buscar el primer arreglo o el primer objeto JSON en el texto
    match = re.search(r"(\[.*\]|\{.*\})", cleaned, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


# ---------------------------------------------------------------------------
# Chat con RAG
# ---------------------------------------------------------------------------

QA_PROMPT = PromptTemplate(
    template="""
Eres un tutor que responde preguntas de estudio usando SOLO el contexto provisto,
extraído de los documentos que subió el usuario.

Responde de forma clara y detallada. Si la respuesta no está en el contexto, di:
"La respuesta no está disponible en el contexto proporcionado."

Contexto:
{context}

Pregunta:
{question}

Respuesta:
""",
    input_variables=["context", "question"],
)


def answer_question(llm, vector_store, question, k=4, return_sources=False):
    docs = vector_store.similarity_search(question, k=k)
    context = "\n\n".join(doc.page_content for doc in docs)
    chain = QA_PROMPT | llm
    answer = _invoke_text(chain, {"context": context, "question": question}).strip()
    if return_sources:
        sources = [doc.page_content for doc in docs]
        return answer, sources
    return answer


# ---------------------------------------------------------------------------
# Extracción de temas del material subido
# ---------------------------------------------------------------------------

TOPIC_EXTRACTION_PROMPT = PromptTemplate(
    template="""
Analiza el siguiente material de estudio y devuelve entre 6 y 12 temas o
conceptos clave que trata, en español.

Reglas:
- Cada tema debe ser corto (2 a 5 palabras).
- No repitas temas ni uses variaciones casi idénticas del mismo concepto.
- Responde ÚNICAMENTE con una lista JSON de strings, sin texto adicional.
  Ejemplo de formato: ["Tema uno", "Tema dos", "Tema tres"]

Material:
{content}
""",
    input_variables=["content"],
)


def extract_topics(llm, full_text, max_chars=9000):
    sample = full_text[:max_chars]
    chain = TOPIC_EXTRACTION_PROMPT | llm
    raw = _invoke_text(chain, {"content": sample})
    parsed = _safe_json_extract(raw)
    if not isinstance(parsed, list):
        return []
    topics = []
    for item in parsed:
        if isinstance(item, str) and item.strip():
            topics.append(item.strip())
    # de-duplicar preservando orden
    seen = set()
    unique_topics = []
    for t in topics:
        key = t.lower()
        if key not in seen:
            seen.add(key)
            unique_topics.append(t)
    return unique_topics


# ---------------------------------------------------------------------------
# Clasificación de preguntas dentro de los temas existentes
# ---------------------------------------------------------------------------

TOPIC_CLASSIFICATION_PROMPT = PromptTemplate(
    template="""
Estos son los temas identificados en el material de estudio:
{topics}

Clasifica la siguiente pregunta del usuario dentro de UNO de esos temas.
Si ninguno encaja razonablemente, responde exactamente: Otro

Responde ÚNICAMENTE con el nombre exacto del tema elegido (tal cual aparece
en la lista) o con la palabra "Otro". No agregues explicaciones.

Pregunta:
{question}
""",
    input_variables=["topics", "question"],
)


def classify_topic(llm, question, topics_list):
    if not topics_list:
        return "General"

    chain = TOPIC_CLASSIFICATION_PROMPT | llm
    topics_text = "\n".join(f"- {t}" for t in topics_list)
    raw = _invoke_text(chain, {"topics": topics_text, "question": question}).strip()
    raw_clean = raw.strip().strip('"').strip("'").strip(".")

    # Coincidencia exacta (insensible a mayúsculas)
    for t in topics_list:
        if t.lower() == raw_clean.lower():
            return t

    # Coincidencia parcial (por si el LLM agrega o quita algo)
    for t in topics_list:
        if t.lower() in raw_clean.lower() or raw_clean.lower() in t.lower():
            return t

    if "otro" in raw_clean.lower():
        return "General"

    return "General"


# ---------------------------------------------------------------------------
# Generación de quizzes adaptativos a partir de los puntos débiles
# ---------------------------------------------------------------------------

QUIZ_GENERATION_PROMPT = PromptTemplate(
    template="""
Eres un generador de quizzes de estudio. Usando ÚNICAMENTE el contexto provisto
(extraído de los documentos del usuario), genera {num_questions} preguntas de
opción múltiple sobre el tema "{topic}" para ayudar al usuario a reforzar ese
punto débil.

Reglas:
- Cada pregunta debe tener exactamente 4 opciones, solo una correcta.
- Varía la posición de la opción correcta entre preguntas.
- Incluye una breve explicación de por qué la respuesta correcta lo es.
- Responde ÚNICAMENTE con JSON válido, con este formato exacto:

[
  {{
    "question": "texto de la pregunta",
    "options": ["opción A", "opción B", "opción C", "opción D"],
    "correct_index": 0,
    "explanation": "breve explicación"
  }}
]

Contexto:
{context}
""",
    input_variables=["topic", "context", "num_questions"],
)


def generate_quiz(llm, vector_store, topic, num_questions=3, k=5):
    docs = vector_store.similarity_search(topic, k=k)
    context = "\n\n".join(doc.page_content for doc in docs)
    if not context.strip():
        return []

    chain = QUIZ_GENERATION_PROMPT | llm
    raw = _invoke_text(
        chain,
        {"topic": topic, "context": context, "num_questions": num_questions},
    )
    parsed = _safe_json_extract(raw)
    if not isinstance(parsed, list):
        return []

    questions = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        question = item.get("question", "").strip()
        options = item.get("options", [])
        correct_index = item.get("correct_index", None)
        explanation = item.get("explanation", "").strip()
        if not question or not isinstance(options, list) or len(options) < 2:
            continue
        try:
            correct_index = int(correct_index)
        except (TypeError, ValueError):
            continue
        if not (0 <= correct_index < len(options)):
            continue
        questions.append(
            {
                "question": question,
                "options": [str(o) for o in options],
                "correct_index": correct_index,
                "explanation": explanation,
            }
        )
    return questions

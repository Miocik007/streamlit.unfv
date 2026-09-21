"""
Capa de persistencia para el sistema de estudio adaptativo.

Guarda en SQLite:
- topics: cada concepto/tema detectado, su frecuencia de consultas y su
  estado de aprendizaje (nuevo -> debil -> reforzado -> dominado).
- questions_log: historial de preguntas hechas al chatbot, con el tema
  al que fueron clasificadas.
- quiz_questions: preguntas de quiz generadas por el LLM a partir de los
  puntos débiles, junto con el resultado cuando el usuario las responde.
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "study_data.db"

# Número de "aciertos netos" que un tema necesita acumular para
# considerarse dominado (y dejar de priorizarse en los quizzes).
MASTERY_TARGET = 3

STATUS_NUEVO = "nuevo"
STATUS_DEBIL = "debil"
STATUS_REFORZADO = "reforzado"
STATUS_DOMINADO = "dominado"

STATUS_LABELS = {
    STATUS_NUEVO: "🆕 Nuevo",
    STATUS_DEBIL: "⚠️ Punto débil",
    STATUS_REFORZADO: "🔄 En refuerzo",
    STATUS_DOMINADO: "✅ Dominado",
}


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                query_count INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                incorrect_count INTEGER DEFAULT 0,
                mastery_score INTEGER DEFAULT 0,
                status TEXT DEFAULT 'nuevo',
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                topic TEXT,
                pdf_names TEXT,
                timestamp TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                question TEXT,
                options TEXT,
                correct_index INTEGER,
                explanation TEXT,
                answered INTEGER DEFAULT 0,
                selected_index INTEGER,
                is_correct INTEGER,
                created_at TEXT,
                answered_at TEXT
            )
        """)


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Temas
# ---------------------------------------------------------------------------

def ensure_topics(topic_names):
    """Inserta los temas que todavía no existen en la base de datos."""
    with get_conn() as conn:
        for name in topic_names:
            name = (name or "").strip()
            if not name:
                continue
            conn.execute(
                """
                INSERT OR IGNORE INTO topics (name, status, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, STATUS_NUEVO, _now(), _now()),
            )


def get_all_topic_names():
    with get_conn() as conn:
        rows = conn.execute("SELECT name FROM topics ORDER BY name ASC").fetchall()
    return [r["name"] for r in rows]


def get_all_topics():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM topics ORDER BY query_count DESC, name ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_weak_topics(limit=5):
    """Temas marcados como punto débil o en refuerzo, priorizados por
    frecuencia de consulta (más preguntados primero) y menor dominio."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM topics
            WHERE status IN (?, ?)
            ORDER BY query_count DESC, mastery_score ASC
            LIMIT ?
            """,
            (STATUS_DEBIL, STATUS_REFORZADO, limit),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Registro de preguntas del chat + detección de puntos débiles
# ---------------------------------------------------------------------------

def log_question(question, answer, topic, pdf_names, threshold):
    """Registra una pregunta del chat, incrementa la frecuencia del tema y
    lo marca como 'punto débil' si supera el umbral configurado.

    Devuelve (nuevo_conteo, nuevo_estado, se_volvio_punto_debil)
    """
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO questions_log (question, answer, topic, pdf_names, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (question, answer, topic, pdf_names, _now()),
        )

        row = conn.execute("SELECT * FROM topics WHERE name = ?", (topic,)).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO topics (name, query_count, status, created_at, updated_at)
                VALUES (?, 0, ?, ?, ?)
                """,
                (topic, STATUS_NUEVO, _now(), _now()),
            )
            row = conn.execute("SELECT * FROM topics WHERE name = ?", (topic,)).fetchone()

        new_count = row["query_count"] + 1
        old_status = row["status"]
        new_status = old_status
        became_weak = False
        if old_status == STATUS_NUEVO and new_count >= threshold:
            new_status = STATUS_DEBIL
            became_weak = True

        conn.execute(
            "UPDATE topics SET query_count = ?, status = ?, updated_at = ? WHERE name = ?",
            (new_count, new_status, _now(), topic),
        )

    return new_count, new_status, became_weak


def get_recent_questions(topic=None, search=None, limit=None):
    """Historial de preguntas del chat, con filtro opcional por tema y por
    texto (busca tanto en la pregunta como en la respuesta). Sin `limit`
    devuelve todo el historial guardado."""
    query = "SELECT * FROM questions_log WHERE 1=1"
    params = []
    if topic:
        query += " AND topic = ?"
        params.append(topic)
    if search:
        query += " AND (question LIKE ? OR answer LIKE ?)"
        like = f"%{search}%"
        params += [like, like]
    query += " ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_daily_query_counts(days=14):
    """Cantidad de preguntas del chat por día (solo días con actividad),
    útil para graficar una tendencia en el Dashboard."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT substr(timestamp, 1, 10) AS day, COUNT(*) AS c
            FROM questions_log
            GROUP BY day
            ORDER BY day ASC
            """
        ).fetchall()
    data = [(r["day"], r["c"]) for r in rows]
    return data[-days:] if days else data


def get_stats_summary():
    """Resumen agregado para tarjetas de estadísticas del Dashboard y de
    Configuración."""
    with get_conn() as conn:
        total_questions = conn.execute(
            "SELECT COUNT(*) AS c FROM questions_log"
        ).fetchone()["c"]
        total_answered = conn.execute(
            "SELECT COUNT(*) AS c FROM quiz_questions WHERE answered = 1"
        ).fetchone()["c"]
        total_correct = conn.execute(
            "SELECT COUNT(*) AS c FROM quiz_questions WHERE answered = 1 AND is_correct = 1"
        ).fetchone()["c"]
        total_topics = conn.execute("SELECT COUNT(*) AS c FROM topics").fetchone()["c"]

    accuracy = round(100 * total_correct / total_answered) if total_answered else 0
    return {
        "total_questions": total_questions,
        "total_answered": total_answered,
        "total_correct": total_correct,
        "accuracy": accuracy,
        "total_topics": total_topics,
    }


# ---------------------------------------------------------------------------
# Quiz adaptativo
# ---------------------------------------------------------------------------

def save_quiz_questions(topic, questions):
    """questions: lista de dicts con question, options (lista), correct_index, explanation"""
    with get_conn() as conn:
        for q in questions:
            options = q.get("options") or []
            conn.execute(
                """
                INSERT INTO quiz_questions (topic, question, options, correct_index, explanation, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    topic,
                    q.get("question", "").strip(),
                    json.dumps(options, ensure_ascii=False),
                    int(q.get("correct_index", 0)),
                    q.get("explanation", "").strip(),
                    _now(),
                ),
            )


def get_pending_quiz_questions(topic=None):
    with get_conn() as conn:
        if topic:
            rows = conn.execute(
                "SELECT * FROM quiz_questions WHERE answered = 0 AND topic = ? ORDER BY id ASC",
                (topic,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM quiz_questions WHERE answered = 0 ORDER BY id ASC"
            ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["options"] = json.loads(d["options"])
        except (TypeError, json.JSONDecodeError):
            d["options"] = []
        result.append(d)
    return result


def get_answered_quiz_questions(topic=None, correctness=None, limit=None):
    """Historial de quizzes respondidos, con filtro opcional por tema y por
    resultado (`correctness`: "correct", "incorrect" o None para todas).
    Sin `limit` devuelve todo el historial guardado."""
    query = "SELECT * FROM quiz_questions WHERE answered = 1"
    params = []
    if topic:
        query += " AND topic = ?"
        params.append(topic)
    if correctness == "correct":
        query += " AND is_correct = 1"
    elif correctness == "incorrect":
        query += " AND is_correct = 0"
    query += " ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["options"] = json.loads(d["options"])
        except (TypeError, json.JSONDecodeError):
            d["options"] = []
        result.append(d)
    return result


def has_pending_quiz_for_topic(topic):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as c FROM quiz_questions WHERE topic = ? AND answered = 0",
            (topic,),
        ).fetchone()
    return row["c"] > 0


def record_quiz_answer(question_id, selected_index):
    """Registra la respuesta del usuario y actualiza dinámicamente el
    estado de aprendizaje del tema asociado:
      - Si acierta: sube el puntaje de dominio; si llega al umbral, el
        tema pasa a 'dominado' y deja de priorizarse.
      - Si falla: baja el puntaje de dominio y el tema vuelve/se mantiene
        como 'punto débil', por lo que se seguirá reforzando en futuros quizzes.
    """
    with get_conn() as conn:
        q = conn.execute(
            "SELECT * FROM quiz_questions WHERE id = ?", (question_id,)
        ).fetchone()
        if q is None:
            return None

        is_correct = 1 if int(selected_index) == q["correct_index"] else 0
        conn.execute(
            """
            UPDATE quiz_questions
            SET answered = 1, selected_index = ?, is_correct = ?, answered_at = ?
            WHERE id = ?
            """,
            (selected_index, is_correct, _now(), question_id),
        )

        topic_row = conn.execute(
            "SELECT * FROM topics WHERE name = ?", (q["topic"],)
        ).fetchone()
        if topic_row:
            mastery = topic_row["mastery_score"]
            correct_count = topic_row["correct_count"]
            incorrect_count = topic_row["incorrect_count"]
            status = topic_row["status"]

            if is_correct:
                mastery += 1
                correct_count += 1
                if mastery >= MASTERY_TARGET:
                    status = STATUS_DOMINADO
                elif status != STATUS_DOMINADO:
                    status = STATUS_REFORZADO
            else:
                mastery = max(0, mastery - 1)
                incorrect_count += 1
                status = STATUS_DEBIL  # fallar reactiva el punto débil

            conn.execute(
                """
                UPDATE topics
                SET mastery_score = ?, correct_count = ?, incorrect_count = ?, status = ?, updated_at = ?
                WHERE name = ?
                """,
                (mastery, correct_count, incorrect_count, status, _now(), q["topic"]),
            )

    return bool(is_correct)


def reset_all():
    with get_conn() as conn:
        conn.execute("DELETE FROM topics")
        conn.execute("DELETE FROM questions_log")
        conn.execute("DELETE FROM quiz_questions")

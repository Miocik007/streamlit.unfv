# 🧠 Sistema de Estudio Adaptativo con PDFs (RAG)

Chatea con tus PDFs, deja que el sistema detecte automáticamente tus puntos
débiles y refuérzalos con quizzes generados por IA.

## ¿Qué hace?

1. **Chat con documentos (RAG):** subes uno o varios PDFs y preguntas sobre
   su contenido. Las respuestas se generan solo con lo que dicen tus
   documentos, y puedes abrir los fragmentos exactos que el modelo usó para
   responder.
2. **Clasificación automática de temas:** al procesar los PDFs, un LLM
   identifica los temas/conceptos clave del material. Cada pregunta que
   haces se clasifica dentro de esos temas.
3. **Detección de puntos débiles:** el sistema cuenta cuántas veces
   preguntas sobre cada tema. Cuando un tema supera un umbral configurable
   de consultas repetidas, se marca automáticamente como **punto débil**.
4. **Quiz adaptativo generado por LLM:** con un clic, se generan preguntas
   de opción múltiple a partir del contenido real de tus documentos,
   enfocadas en tus puntos débiles.
5. **Estado de aprendizaje dinámico:** si respondes bien un tema, sube su
   "dominio" hasta considerarse **dominado** (deja de priorizarse). Si
   fallas, el tema vuelve a marcarse como punto débil y se refuerza en el
   próximo quiz.
6. **Historial persistente y buscable:** todas tus preguntas y respuestas de
   quiz quedan guardadas en SQLite, no solo en la sesión del navegador, y se
   pueden filtrar, buscar y exportar a CSV.

## Páginas de la app

La app está organizada como una aplicación multipágina (navegación en la
barra lateral), no como pestañas dentro de una sola pantalla:

- **💬 Chat** — conversa con tus documentos.
- **📊 Dashboard** — estado de cada tema, precisión global, tendencia de
  preguntas por día, y una grilla de temas filtrable/ordenable.
- **🧠 Quiz adaptativo** — genera y responde quizzes sobre tus puntos
  débiles.
- **🕘 Historial** — historial completo (no solo de la sesión actual) de
  preguntas del chat y de quizzes respondidos, con filtros por tema,
  búsqueda de texto y exportación a CSV.
- **⚙️ Configuración** — API Key y modelo (con botón para verificar la
  conexión), carga/reprocesamiento de documentos, parámetros de aprendizaje
  adaptativo, y reinicio de progreso (con confirmación explícita).

## Instalación

```bash
python -m venv myenv
source myenv/bin/activate   # Windows: myenv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

Necesitas una API Key de Google AI Studio (Gemini):
https://ai.google.dev/

Se ingresa en la página **⚙️ Configuración** (no se guarda en disco).

## Ejecutar

```bash
streamlit run app.py
```

1. Ve a **⚙️ Configuración**: ingresa tu API Key de Google, sube uno o
   varios PDFs y presiona **Procesar documentos**.
2. Ve a **💬 Chat** y haz preguntas sobre el contenido.
3. Revisa **📊 Dashboard** para ver tus temas, frecuencia de consultas,
   tendencia por día y estado (nuevo / punto débil / en refuerzo /
   dominado).
4. En **🧠 Quiz adaptativo**, genera un quiz basado en tus puntos débiles y
   respóndelo. Tu desempeño actualiza tu estado de aprendizaje.
5. En **🕘 Historial**, revisa o exporta todo lo que has preguntado y
   respondido.

## Estructura del proyecto

```
app.py               -> Punto de entrada: configuración de página y
                         navegación multipágina (st.navigation)
state.py             -> Estado de sesión compartido entre páginas y acceso
                         al LLM configurado
views/
  chat.py            -> Página: Chat con los documentos (RAG + fuentes)
  dashboard.py        -> Página: Dashboard de progreso (stats, tendencia,
                         grilla de temas filtrable)
  quiz.py            -> Página: Quiz adaptativo
  history.py         -> Página: Historial persistente (búsqueda, filtros,
                         exportación a CSV)
  settings.py        -> Página: Configuración (modelo, documentos,
                         parámetros, datos)
rag_engine.py        -> Procesamiento de PDFs, vectorstore FAISS, chains del
                         LLM (respuesta + fuentes, extracción de temas,
                         clasificación, quizzes)
db.py                -> Persistencia SQLite: temas, frecuencia, estado de
                         aprendizaje, historial de preguntas y quizzes
                         (con búsqueda, filtros y estadísticas agregadas)
theme.py             -> Sistema de diseño: paleta, tipografía, CSS y
                         componentes HTML (insignias, tarjetas, barras,
                         estados vacíos, estado del sistema en la barra
                         lateral)
.streamlit/config.toml -> Tema base de Streamlit (colores del framework)
requirements.txt
```

## Diseño

El dashboard usa una identidad propia en vez de la plantilla por defecto de
Streamlit: tipografía serif (Source Serif 4) para títulos y sans-serif (IBM
Plex Sans) para el resto, paleta en tonos tinta/verde-bosque/ámbar, y un
trazo de color a la izquierda de cada bloque —chat, tarjetas de tema,
formularios de quiz— que indica su estado (punto débil, en refuerzo,
dominado), como las anotaciones al margen de un cuaderno de estudio.
Todo el CSS vive en `theme.py`; para ajustar colores o tipografía, ese es
el único archivo que hace falta tocar.

La barra lateral muestra la marca, un estado del sistema (API conectada /
documentos cargados) siempre visible, y debajo la navegación entre páginas
agrupada en "Estudiar" y "Sistema".

El progreso (temas, dominio, historial) se guarda en `study_data.db`
(SQLite) y persiste entre sesiones. Puedes reiniciarlo desde **⚙️
Configuración → Datos** (pide confirmación explícita antes de borrar).

## Notas técnicas

- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace, local).
- Vector store: FAISS, en memoria por sesión (se reconstruye al procesar
  documentos).
- LLM: Google Gemini vía `langchain-google-genai`. El nombre del modelo es
  configurable en **⚙️ Configuración** (por defecto `gemini-2.5-flash`); si
  tu cuenta no tiene acceso a ese modelo, cámbialo por el que sí tengas
  disponible en tu API Key.
- Umbral de puntos débiles, cantidad de preguntas por quiz y cantidad de
  temas por tanda de quiz son configurables desde **⚙️ Configuración**.
- Requiere Streamlit 1.36 o superior (por `st.navigation`/`st.Page`); el
  `requirements.txt` no fija versión, así que una instalación nueva ya
  cumple esto.

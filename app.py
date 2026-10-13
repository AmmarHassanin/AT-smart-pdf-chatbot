import hashlib
import json
import os
import re
import warnings
from io import BytesIO

warnings.filterwarnings(
    "ignore",
    message=r"`langchain-community` is being sunset",
    category=DeprecationWarning,
)

import streamlit as st
from dotenv import load_dotenv
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

MODELS = {
    "GPT-OSS 120B — أدق": "openai/gpt-oss-120b",
    "GPT-OSS 20B — أسرع": "openai/gpt-oss-20b",
}

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            "You are AT, a document assistant. Answer using only the context below.\n"
            "Rules:\n"
            "- Reply in the same language as the current question. "
            "An English question gets an English answer, and an Arabic question gets an Arabic answer.\n"
            "- If the context does not contain the answer, say so in that same language "
            "and do not guess.\n"
            "- Mention the file name and page number when that helps.\n"
            "- Do not add facts from outside the context.\n\n"
            "Context:\n{context}\n\n"
            "{input}",
        )
    ]
)

DOCUMENT_PROMPT = ChatPromptTemplate.from_template(
    "File: {source} | Page: {page}\n{page_content}"
)

THINK_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL)


def clean_answer(text: str) -> str:
    return THINK_PATTERN.sub("", text or "").strip()


def file_signature(files) -> str:
    digest = hashlib.sha256()
    for file in files:
        digest.update(file.name.encode("utf-8", errors="replace"))
        digest.update(b"\0")
        digest.update(file.getvalue())
    return digest.hexdigest()


def read_pdf(file) -> tuple[list[Document], int, str | None]:
    try:
        reader = PdfReader(BytesIO(file.getvalue()))
    except Exception as error:
        return [], 0, f"تعذر قراءة {file.name}: {error}"

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            return [], 0, f"{file.name} محمي بكلمة مرور، ارفع نسخة غير مشفرة."

    documents = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            extracted = page.extract_text() or ""
        except Exception:
            extracted = ""
        text = extracted.strip()
        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": file.name, "page": index},
                )
            )
    return documents, len(reader.pages), None


def build_index(files, embeddings):
    documents = []
    pages = 0
    warnings_list = []

    for file in files:
        file_docs, file_pages, warning = read_pdf(file)
        pages += file_pages
        documents.extend(file_docs)
        if warning:
            warnings_list.append(warning)

    if not documents:
        return None, {"pages": pages, "chunks": 0, "files": len(files)}, warnings_list

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    store = FAISS.from_documents(chunks, embeddings)
    stats = {"pages": pages, "chunks": len(chunks), "files": len(files)}
    return store, stats, warnings_list


@st.cache_resource(show_spinner=False)
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        encode_kwargs={"normalize_embeddings": True},
    )


@st.cache_resource(show_spinner=False)
def load_llm(model_name: str, effort: str):
    return ChatGroq(
        model=model_name,
        temperature=0.6,
        max_tokens=4096,
        reasoning_format="hidden",
        reasoning_effort=effort,
        model_kwargs={"top_p": 0.95},
    )


def recent_history(messages, limit: int = 6) -> str:
    lines = []
    for message in messages[-limit:]:
        speaker = "User" if message["role"] == "user" else "AT"
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)


def render_sources(sources):
    if not sources:
        return
    with st.expander("المقاطع المستخدمة"):
        for source in sources:
            st.markdown(f"**{source['source']}** — صفحة {source['page']}")
            st.caption(source["snippet"])


def answer_question(question: str, store, llm, messages, k: int):
    retriever = store.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)
    history = recent_history(messages)
    composed = question
    if history:
        composed = f"Previous conversation:\n{history}\n\nCurrent question: {question}"

    chain = create_stuff_documents_chain(
        llm,
        ANSWER_PROMPT,
        document_prompt=DOCUMENT_PROMPT,
    )

    def token_stream():
        for chunk in chain.stream({"input": composed, "context": docs}):
            if isinstance(chunk, str) and chunk:
                yield chunk

    return token_stream, docs


def handle_question(question: str, store, model_label: str, k: int) -> None:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="💬"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            llm = load_llm(MODELS[model_label], "high")
            token_stream, docs = answer_question(
                question,
                store,
                llm,
                st.session_state.messages[:-1],
                k,
            )
            raw_answer = st.write_stream(token_stream)
        except Exception as error:
            st.error(f"تعذر توليد الإجابة: {error}")
            return

        answer = clean_answer(raw_answer)
        if not answer:
            answer = "لم تصل إجابة من النموذج. أعد المحاولة."
            st.markdown(answer)

        sources = [
            {
                "source": doc.metadata.get("source", "PDF"),
                "page": doc.metadata.get("page", "—"),
                "snippet": doc.page_content[:280].replace("\n", " "),
            }
            for doc in docs
        ]
        render_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )


st.set_page_config(
    page_title="AT - Smart PDF Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto",
)

load_dotenv()

DASHBOARD_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;600;700;800&display=swap');

    :root {
        --bg-deep: #050608;
        --bg-panel: rgba(12, 14, 20, 0.72);
        --gold: #f5c451;
        --gold-soft: rgba(245, 196, 81, 0.35);
        --gold-glow: rgba(255, 214, 102, 0.55);
        --text-main: #f4f4f5;
        --text-muted: #a1a1aa;
        --border-glass: rgba(245, 196, 81, 0.22);
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Cairo", sans-serif;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"], section.main {
        overflow-x: hidden;
        max-width: 100%;
    }

    .stApp {
        background:
            radial-gradient(ellipse 80% 50% at 50% -10%, rgba(245, 196, 81, 0.08), transparent 55%),
            linear-gradient(180deg, #07080c 0%, #050608 45%, #030304 100%);
        color: var(--text-main);
    }

    header[data-testid="stHeader"] {
        background: transparent;
        visibility: hidden;
        height: 0;
        min-height: 0;
    }

    [data-testid="stSidebar"] {
        background: rgba(8, 9, 12, 0.92) !important;
        backdrop-filter: blur(18px);
        border-right: 1px solid var(--border-glass);
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow-y: auto !important;
        padding-bottom: 48px;
    }

    .sidebar-brand {
        text-align: center;
        padding: 8px 4px 14px;
        border-bottom: 1px solid var(--border-glass);
        margin-bottom: 12px;
    }

    .sidebar-brand h2 {
        margin: 6px 0 2px;
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--gold);
        letter-spacing: 0.06em;
    }

    .sidebar-brand p {
        margin: 0;
        color: var(--text-muted);
        font-size: 0.82rem;
    }

    .project-nav-title {
        color: var(--text-muted);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        margin: 10px 0 8px;
        text-transform: uppercase;
    }

    .project-btn {
        display: block;
        width: 100%;
        text-align: left;
        direction: ltr;
        margin-bottom: 8px;
        padding: 10px 12px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(255, 255, 255, 0.03);
        color: #d4d4d8;
        font-size: 0.86rem;
        font-weight: 600;
        line-height: 1.35;
    }

    .project-btn.active {
        border-color: var(--gold-soft);
        background: linear-gradient(90deg, rgba(245, 196, 81, 0.16), rgba(245, 196, 81, 0.04));
        color: var(--gold);
    }

    .hero-title {
        font-size: clamp(1.6rem, 3vw, 2.35rem);
        font-weight: 800;
        letter-spacing: 0.04em;
        color: var(--gold);
        margin: 0 0 8px;
        line-height: 1.15;
    }

    .hero-sub {
        direction: rtl;
        text-align: right;
        color: var(--text-main);
        font-size: 1.05rem;
        font-weight: 600;
        margin: 0;
        max-width: 520px;
    }

    .glass-card {
        background: var(--bg-panel);
        backdrop-filter: blur(14px);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        padding: 18px 20px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
        min-height: 100%;
    }

    .card-title {
        margin: 0 0 14px;
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--gold);
        letter-spacing: 0.03em;
    }

    .feature-list {
        list-style: none;
        margin: 0;
        padding: 0;
        direction: rtl;
    }

    .feature-list li {
        display: flex;
        align-items: center;
        gap: 10px;
        justify-content: flex-end;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        color: var(--text-main);
        font-size: 0.95rem;
        font-weight: 600;
    }

    .feature-list li:last-child { border-bottom: none; }

    .feature-icon {
        color: var(--gold);
        font-size: 1.05rem;
    }

    .pdf-drop-label {
        direction: rtl;
        text-align: center;
        color: var(--text-muted);
        font-size: 0.88rem;
        margin: 0 0 8px;
    }

    [data-testid="stMain"] iframe {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        width: 100% !important;
        max-width: 100%;
    }

    [data-testid="stFileUploader"] {
        width: 100%;
        background: rgba(255, 255, 255, 0.02);
        border: 2px dashed var(--gold-soft);
        border-radius: 16px;
        padding: 14px;
    }

    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploaderDropzone"] * {
        color: var(--text-main) !important;
        opacity: 1 !important;
    }

    div[data-testid="stForm"] {
        margin-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 10px;
    }

    div[data-testid="stForm"] input {
        width: 100% !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid var(--border-glass) !important;
        color: var(--text-main) !important;
        border-radius: 12px !important;
        min-height: 2.75rem;
        font-size: 1rem !important;
    }

    div[data-testid="stForm"] button[kind="secondaryFormSubmit"],
    div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
        background: linear-gradient(90deg, #f5c451, #ffd978) !important;
        color: #111 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        box-shadow: 0 0 16px var(--gold-glow);
        min-height: 2.75rem;
    }

    section.main [data-testid="column"] .stButton > button {
        min-height: 2.75rem;
        border-radius: 12px !important;
    }

    .control-bar-spacer {
        height: 1.6rem;
    }

    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
    }

    [data-testid="stChatMessageContent"] {
        unicode-bidi: plaintext;
        text-align: start;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 8px 10px;
    }

    section.main [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--bg-panel);
        backdrop-filter: blur(14px);
        border: 1px solid var(--border-glass) !important;
        border-radius: 14px;
        margin-bottom: 16px;
        padding: 6px 10px 2px;
    }

    section.main [data-testid="stVerticalBlockBorderWrapper"] label,
    section.main [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] p {
        color: var(--text-muted) !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stBottom"] { display: none !important; }

    [data-testid="stMain"] .block-container {
        padding-top: 1.2rem;
        padding-bottom: 4.8rem;
        padding-left: clamp(0.75rem, 2vw, 1.5rem);
        padding-right: clamp(0.75rem, 2vw, 1.5rem);
        max-width: min(1180px, 100%);
    }

    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        z-index: 1002;
    }

    .page-footer {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 1000;
        text-align: center;
        padding: 10px 16px;
        background: rgba(5, 6, 8, 0.94);
        border-top: 1px solid var(--border-glass);
        color: #e4e4e7;
        font-weight: 700;
        backdrop-filter: blur(12px);
    }

    .footer-dev-link {
        color: #e4e4e7;
        text-decoration: none;
        font-weight: 700;
        padding: 0.25rem 0.5rem;
        border-radius: 8px;
        transition: color 0.2s ease, background 0.2s ease;
    }

    .footer-dev-link:hover {
        color: var(--gold);
        background: rgba(245, 196, 81, 0.08);
        text-decoration: underline;
        text-underline-offset: 3px;
    }

    .api-key-quiet {
        position: absolute;
        right: 14px;
        top: 50%;
        transform: translateY(-50%);
        font-family: Consolas, "Courier New", monospace;
        font-size: 9px;
        color: rgba(245, 196, 81, 0.28);
    }

    @media (max-width: 1024px) {
        [data-testid="stMain"] .block-container {
            padding-bottom: 5.2rem;
        }

        .hero-sub {
            max-width: 100%;
        }
    }

    @media (max-width: 768px) {
        section.main [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            flex-wrap: wrap !important;
            gap: 0.85rem !important;
            width: 100% !important;
        }

        section.main [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
        }

        section.main [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 0.65rem 0.55rem 0.35rem;
        }

        .hero-title {
            font-size: clamp(1.25rem, 5vw, 1.75rem);
            text-align: center;
        }

        .hero-sub {
            text-align: center;
            margin-inline: auto;
            font-size: 0.95rem;
        }

        [data-testid="stMain"] iframe {
            height: 9.5rem !important;
            max-height: 38vh;
        }

        .glass-card {
            padding: 0.9rem;
            border-radius: 1rem;
            min-height: auto;
        }

        .card-title {
            font-size: 0.98rem;
        }

        .feature-list li {
            font-size: 0.9rem;
            padding: 0.65rem 0;
        }

        [data-testid="stFileUploader"],
        [data-testid="stFileUploaderDropzone"],
        div[data-testid="stForm"],
        [data-testid="stSelectbox"],
        [data-testid="stSlider"] {
            width: 100% !important;
            max-width: 100% !important;
        }

        [data-testid="stMetric"] {
            margin-bottom: 0.35rem;
        }

        div[data-testid="stForm"] button[kind="secondaryFormSubmit"],
        div[data-testid="stForm"] button[kind="primaryFormSubmit"],
        section.main [data-testid="column"] .stButton > button {
            width: 100% !important;
        }

        .control-bar-spacer {
            display: none;
            height: 0;
            margin: 0;
        }

        .page-footer {
            font-size: 0.9rem;
            padding: 0.65rem 0.75rem 0.75rem;
        }

        .api-key-quiet {
            position: static;
            display: block;
            margin-top: 0.15rem;
            transform: none;
        }

        [data-testid="stSidebar"] {
            width: min(86vw, 19rem) !important;
            max-width: 86vw !important;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding-bottom: 1.5rem;
        }
    }

    @media (max-width: 480px) {
        [data-testid="stMain"] iframe {
            height: 7.5rem !important;
            max-height: 32vh;
        }

        [data-testid="stMain"] .block-container {
            padding-top: 0.85rem;
            padding-bottom: 5.5rem;
        }

        .project-btn {
            font-size: 0.8rem;
            padding: 0.65rem 0.75rem;
        }
    }
</style>
<div class="page-footer">
  <a class="footer-dev-link" href="https://ammarhassanin.github.io/portf0lio/" target="_blank" rel="noopener noreferrer">Developed by Ammar Yasser</a>
  <span class="api-key-quiet">GROQ_API_KEY</span>
</div>
"""

st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_signature" not in st.session_state:
    st.session_state.doc_signature = None
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "stats" not in st.session_state:
    st.session_state.stats = None
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div style="font-size:2rem;">🤖</div>
            <h2>AT BOT</h2>
            <p>Smart PDF Chatbot Dashboard</p>
        </div>
        <div class="project-nav-title">Projects</div>
        <div class="project-btn active">1. Smart PDF Chatbot</div>
        <div class="project-btn">2. Advanced Data Analysis</div>
        <div class="project-btn">3. Machine Learning Modelling</div>
        """,
        unsafe_allow_html=True,
    )

ROBOT_HTML = """
<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"></script>
<style>
  html, body {
    margin: 0;
    height: 12.5rem;
    overflow: hidden;
    background: transparent !important;
  }
  .viewer-wrap {
    height: 12.5rem;
    background: transparent;
    border: none;
    box-shadow: none;
  }
  model-viewer {
    width: 100%;
    height: 12.5rem;
    background: transparent;
    --poster-color: transparent;
    border: none;
    box-shadow: none;
    filter: sepia(0.35) saturate(1.45) hue-rotate(5deg) brightness(1.08);
  }
  .progress { display: none !important; }
  @media (max-width: 768px) {
    html, body, .viewer-wrap, model-viewer { height: 9.5rem; max-height: 38vh; }
  }
  @media (max-width: 480px) {
    html, body, .viewer-wrap, model-viewer { height: 7.5rem; max-height: 32vh; }
  }
</style>
</head>
<body>
  <div class="viewer-wrap">
    <model-viewer
      id="at-robot"
      src="https://cdn.jsdelivr.net/gh/mrdoob/three.js@r170/examples/models/gltf/RobotExpressive/RobotExpressive.glb"
      camera-orbit="18deg 78deg 135%"
      field-of-view="36deg"
      disable-zoom
      disable-pan
      interaction-prompt="none"
      shadow-intensity="0"
      exposure="1.15"
      alt="روبوت AT"
    ></model-viewer>
  </div>
  <script>
    const robot = document.getElementById("at-robot");
    function waveThenIdle() {
      const names = robot.availableAnimations || [];
      const wave = names.find((name) => /wave/i.test(name));
      const idle = names.find((name) => /idle/i.test(name));
      if (!wave) return;
      robot.animationName = wave;
      try { robot.play({ repetitions: 1 }); } catch (error) { robot.play(); }
      const done = () => {
        robot.removeEventListener("finished", done);
        if (!idle) return;
        robot.animationName = idle;
        try { robot.play({ repetitions: Infinity }); } catch (error) { robot.play(); }
      };
      robot.addEventListener("finished", done);
    }
    robot.addEventListener("load", waveThenIdle);
    robot.addEventListener("click", waveThenIdle);
  </script>
</body>
</html>
"""

hero_robot, hero_text = st.columns([1.15, 1], vertical_alignment="center", gap="medium")
with hero_robot:
    st.iframe(ROBOT_HTML, height=200)
with hero_text:
    st.markdown(
        """
        <div class="hero-title">AT - SMART PDF CHATBOT</div>
        <div class="hero-sub">مشروع ذكي لقراءة ملفات PDF وملخصها. جرب الآن!</div>
        """,
        unsafe_allow_html=True,
    )

if not os.getenv("GROQ_API_KEY"):
    st.error("أضف GROQ_API_KEY في ملف .env ثم أعد تشغيل التطبيق.")
    st.stop()

with st.container(border=True):
    control_model, control_k, control_clear = st.columns([1.1, 1.1, 0.55], gap="medium")
    with control_model:
        model_label = st.selectbox("النموذج", list(MODELS))
    with control_k:
        k = st.slider("عدد المقاطع المسترجعة", min_value=2, max_value=8, value=4)
    with control_clear:
        st.markdown('<div class="control-bar-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)
        if st.button("مسح المحادثة", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()

pdfs = None
insight_col, upload_col = st.columns(2, gap="medium", vertical_alignment="top")
with insight_col:
    st.markdown(
        """
        <div class="glass-card">
            <h3 class="card-title">PDF Insight</h3>
            <ul class="feature-list">
                <li><span class="feature-icon">📄</span><span>قراءة ملفات PDF بدقة</span></li>
                <li><span class="feature-icon">✨</span><span>ملخصات ذكية من محتوى الملف</span></li>
                <li><span class="feature-icon">⚡</span><span>إجابات سريعة مربوطة بالنص</span></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
with upload_col:
    st.markdown(
        """
        <div class="glass-card">
            <h3 class="card-title">Upload and Summarize</h3>
            <p class="pdf-drop-label">📑 اسحب ملف PDF أو اضغط Upload</p>
        """,
        unsafe_allow_html=True,
    )
    pdfs = st.file_uploader(
        "PDF",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="ارفع ملف PDF فيه نص قابل للتحديد.",
    )
    with st.form("question_form", clear_on_submit=True):
        question_input = st.text_input(
            "question",
            placeholder="اكتب سؤالك هنا..",
            label_visibility="collapsed",
        )
        send_question = st.form_submit_button("إرسال", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if send_question and question_input.strip():
        if st.session_state.vector_store is None:
            st.warning("ارفع ملف PDF فيه نص أولاً، ثم أعد إرسال السؤال.")
        else:
            st.session_state.pending_question = question_input.strip()
            st.rerun()

if pdfs:
    signature = file_signature(pdfs)
    if signature != st.session_state.doc_signature:
        with st.spinner("جاري قراءة الملف وبناء الفهرس..."):
            try:
                store, stats, index_warnings = build_index(pdfs, load_embeddings())
            except Exception as error:
                st.error(f"تعذر فهرسة الملفات: {error}")
                st.stop()
        st.session_state.vector_store = store
        st.session_state.stats = stats
        st.session_state.doc_signature = signature
        st.session_state.messages = []
        st.session_state.index_warnings = index_warnings

for warning in st.session_state.get("index_warnings", []):
    st.warning(warning)

store = st.session_state.vector_store
stats = st.session_state.stats or {"files": 0, "pages": 0, "chunks": 0}

if store is not None:
    files_col, pages_col, chunks_col = st.columns(3)
    files_col.metric("الملفات", stats["files"])
    pages_col.metric("الصفحات", stats["pages"])
    chunks_col.metric("المقاطع", stats["chunks"])

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "💬"):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_sources(message.get("sources") or [])

    if st.session_state.pending_question:
        handle_question(st.session_state.pending_question, store, model_label, k)
        st.session_state.pending_question = None
elif pdfs:
    st.error("لم يُستخرج نص من الملفات. تأكد أن الـ PDF يحتوي نصًا وليس صورًا فقط.")

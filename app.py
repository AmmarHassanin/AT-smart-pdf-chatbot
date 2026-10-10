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


st.set_page_config(
    page_title="AT - Smart PDF Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

st.markdown(
    """
<style>
    .stApp {
        background: radial-gradient(circle at 50% -20%, #2e1065 0%, #090514 60%, #030008 100%);
        color: #f3e8ff;
    }

    [data-testid="stSidebar"] {
        background: rgba(15, 7, 32, 0.78) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(168, 85, 247, 0.25);
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        height: calc(100vh - 58px) !important;
        max-height: calc(100vh - 58px) !important;
        overflow-y: auto !important;
        box-sizing: border-box;
        padding-bottom: 12px;
    }

    .hero-title {
        font-size: 5.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #c084fc, #a855f7, #e879f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: left;
        line-height: 0.95;
        margin: 0 0 8px;
    }

    .hero-kicker {
        color: #e9d5ff;
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        margin-bottom: 12px;
    }

    .hero-sub {
        text-align: right;
        direction: rtl;
        color: #d8b4fe;
        font-size: 1.05rem;
        margin-bottom: 8px;
        max-width: 460px;
    }

    [data-testid="stCustomComponentV1"],
    [data-testid="stMain"] iframe {
        background: transparent !important;
        border: none !important;
    }

    [data-testid="stFileUploader"] {
        background: rgba(88, 28, 135, 0.15);
        border: 2px dashed #a855f7;
        border-radius: 20px;
        padding: 18px;
    }

    [data-testid="stChatMessage"] {
        background: rgba(88, 28, 135, 0.16);
        border: 1px solid rgba(168, 85, 247, 0.22);
        border-radius: 16px;
        padding: 4px 8px;
    }

    [data-testid="stChatMessageContent"] {
        unicode-bidi: plaintext;
        text-align: start;
    }

    .developer-name {
        background: linear-gradient(90deg, #f0abfc, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 20px;
    }

    .page-footer {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 1000;
        text-align: center;
        padding: 12px 16px;
        background: rgba(9, 5, 20, 0.92);
        border-top: 1px solid rgba(168, 85, 247, 0.35);
        color: #f3e8ff;
        font-weight: 700;
        letter-spacing: 0.4px;
        backdrop-filter: blur(12px);
    }

    .api-key-quiet {
        position: absolute;
        right: 14px;
        top: 50%;
        transform: translateY(-50%);
        font-family: Consolas, "Courier New", monospace;
        font-size: 9px;
        font-weight: 400;
        letter-spacing: 0;
        color: rgba(216, 180, 254, 0.35);
    }

    [data-testid="stBottom"] {
        bottom: 48px !important;
    }

    [data-testid="stMain"] .block-container {
        padding-bottom: 4.5rem;
    }
</style>
<div class="page-footer">Ammar yasser<span class="api-key-quiet">GROQ_API_KEY</span></div>
""",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_signature" not in st.session_state:
    st.session_state.doc_signature = None
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "stats" not in st.session_state:
    st.session_state.stats = None

with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 8px;">
            <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Writing%20Hand.png" width="70" alt="AT">
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("AT Bot")
    st.markdown(
        """
        **AT - Smart PDF Chatbot**  
        اسأل ملفات PDF بالعربية أو الإنجليزية، والإجابة تطلع من النص نفسه.

        👨‍💻 **Developed by:**  
        <span class="developer-name">Ammar Yasser</span>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    model_label = st.selectbox("النموذج", list(MODELS))
    effort = st.select_slider(
        "عمق التفكير",
        options=["low", "medium", "high"],
        value="low",
        help="low أسرع للأسئلة المباشرة. high أنسب للأسئلة التي تحتاج ربط أكثر من مقطع.",
    )
    k = st.slider("عدد المقاطع المسترجعة", min_value=2, max_value=8, value=4)
    if st.button("مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

INTRO_TEXT = (
    "أهلًا، أنا AT.\n"
    "روبوتك الذكي لقراءة ملفات PDF.\n"
    "ارفع الملف واسألني، وهجاوبك من جوه النص."
)
SPEECH_TEXT = (
    "أهلًا. أنا إي تي. روبوتك الذكي لقراءة ملفات البي دي إف. "
    "ارفع الملف واسألني، وهجاوبك من جوه النص."
)

ROBOT_HTML = """
<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="utf-8" />
<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"></script>
<style>
  html, body {
    margin: 0;
    height: 440px;
    overflow: hidden;
    background: transparent;
    color: #f3e8ff;
    font-family: "Segoe UI", Tahoma, sans-serif;
  }
  .stage {
    display: grid;
    grid-template-columns: 1.15fr 0.95fr;
    align-items: center;
    height: 440px;
    position: relative;
  }
  .viewer-wrap {
    position: relative;
    height: 420px;
  }
  .glow {
    position: absolute;
    left: 50%;
    top: 54%;
    width: 210px;
    height: 210px;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(168, 85, 247, 0.55), transparent 68%);
    filter: blur(6px);
    pointer-events: none;
  }
  model-viewer {
    width: 100%;
    height: 420px;
    background: transparent;
    --poster-color: transparent;
    position: relative;
    z-index: 1;
  }
  .progress {
    position: absolute;
    left: 18%;
    right: 18%;
    bottom: 28px;
    height: 4px;
    border-radius: 99px;
    background: rgba(168, 85, 247, 0.25);
    overflow: hidden;
  }
  .bar {
    height: 100%;
    width: 0;
    background: linear-gradient(90deg, #c084fc, #e879f9);
  }
  .bubble {
    position: relative;
    background: rgba(24, 9, 43, 0.78);
    border: 1px solid rgba(192, 132, 252, 0.45);
    border-radius: 18px;
    padding: 16px 16px 12px;
    line-height: 1.75;
    font-size: 16px;
    min-height: 148px;
    box-shadow: 0 0 28px rgba(168, 85, 247, 0.28);
    white-space: pre-line;
    direction: rtl;
  }
  .bubble:before {
    content: "";
    position: absolute;
    left: -11px;
    top: 46px;
    border-width: 9px 12px 9px 0;
    border-style: solid;
    border-color: transparent rgba(192, 132, 252, 0.7) transparent transparent;
  }
  .caret {
    display: inline-block;
    width: 8px;
    height: 1em;
    margin-right: 2px;
    background: #e879f9;
    vertical-align: text-bottom;
    animation: blink 0.9s steps(1) infinite;
  }
  .caret[hidden] { display: none; }
  @keyframes blink { 50% { opacity: 0; } }
  button {
    margin-top: 10px;
    background: transparent;
    color: #e9d5ff;
    border: 1px solid rgba(192, 132, 252, 0.55);
    border-radius: 999px;
    padding: 6px 12px;
    cursor: pointer;
    font-family: inherit;
    font-size: 13px;
  }
  button:hover { background: rgba(168, 85, 247, 0.25); }
  .fallback {
    height: 420px;
    display: grid;
    place-items: center;
    perspective: 700px;
  }
  .bot {
    transform-style: preserve-3d;
    animation: spin 7s linear infinite;
    filter: drop-shadow(0 0 18px rgba(168, 85, 247, 0.8));
  }
  @keyframes spin {
    from { transform: rotateY(0deg) translateY(0); }
    50% { transform: rotateY(180deg) translateY(-10px); }
    to { transform: rotateY(360deg) translateY(0); }
  }
  .head, .torso {
    background: linear-gradient(160deg, #f5d0fe, #7e22ce);
    border-radius: 16px;
    margin: 0 auto;
  }
  .head { width: 86px; height: 72px; position: relative; }
  .torso { width: 104px; height: 78px; margin-top: 8px; border-radius: 20px; }
  .eye {
    position: absolute;
    top: 26px;
    width: 14px;
    height: 14px;
    background: #090514;
    border-radius: 50%;
    box-shadow: 0 0 10px #67e8f9;
  }
  .eye.l { left: 18px; }
  .eye.r { right: 18px; }
  .antenna {
    width: 4px;
    height: 22px;
    background: #e879f9;
    margin: 0 auto 4px;
    position: relative;
  }
  .antenna:before {
    content: "";
    position: absolute;
    top: -8px;
    left: -5px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #f0abfc;
  }
</style>
</head>
<body>
  <div class="stage">
    <div class="viewer-wrap">
      <div class="glow"></div>
      <model-viewer
        id="at-robot"
        src="https://cdn.jsdelivr.net/gh/mrdoob/three.js@r170/examples/models/gltf/RobotExpressive/RobotExpressive.glb"
        camera-orbit="18deg 78deg auto"
        auto-rotate
        rotation-per-second="18deg"
        camera-controls
        disable-zoom
        disable-pan
        interaction-prompt="none"
        shadow-intensity="1.1"
        exposure="1.25"
        environment-image="neutral"
        alt="روبوت AT ثلاثي الأبعاد"
      >
        <div class="progress" slot="progress-bar"><div class="bar"></div></div>
      </model-viewer>
      <div id="fallback" class="fallback" hidden>
        <div class="bot">
          <div class="antenna"></div>
          <div class="head"><div class="eye l"></div><div class="eye r"></div></div>
          <div class="torso"></div>
        </div>
      </div>
    </div>
    <div class="bubble">
      <span id="line"></span><span id="caret" class="caret"></span>
      <div><button id="speak" type="button">اسمع التعريف</button></div>
    </div>
  </div>
  <script>
    const intro = __INTRO_JSON__;
    const speechText = __SPEECH_JSON__;
    const playIntro = __PLAY_INTRO__;
    const line = document.getElementById("line");
    const caret = document.getElementById("caret");
    const robot = document.getElementById("at-robot");
    const fallback = document.getElementById("fallback");
    let typing = null;

    function showFallback() {
      robot.hidden = true;
      fallback.hidden = false;
    }

    robot.addEventListener("error", showFallback);
    robot.addEventListener("progress", (event) => {
      const bar = document.querySelector(".bar");
      const progress = event.detail.totalProgress || 0;
      if (bar) bar.style.width = (progress * 100) + "%";
      const box = document.querySelector(".progress");
      if (box && progress >= 1) box.style.display = "none";
    });

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

    function speak() {
      if (!window.speechSynthesis) return;
      const utter = new SpeechSynthesisUtterance(speechText);
      utter.lang = "ar";
      utter.rate = 0.95;
      const voice = speechSynthesis.getVoices().find((item) => item.lang && item.lang.toLowerCase().startsWith("ar"));
      if (voice) utter.voice = voice;
      speechSynthesis.cancel();
      speechSynthesis.speak(utter);
    }

    function typeIntro() {
      if (typing) clearInterval(typing);
      line.textContent = "";
      caret.hidden = false;
      let index = 0;
      typing = setInterval(() => {
        line.textContent += intro[index];
        index += 1;
        if (index >= intro.length) {
          clearInterval(typing);
          caret.hidden = true;
        }
      }, 32);
    }

    function showFull() {
      line.textContent = intro;
      caret.hidden = true;
    }

    function replay(withVoice) {
      typeIntro();
      waveThenIdle();
      if (withVoice) {
        if (speechSynthesis.getVoices().length) speak();
        else speechSynthesis.addEventListener("voiceschanged", speak, { once: true });
      }
    }

    document.getElementById("speak").addEventListener("click", () => replay(true));
    robot.addEventListener("click", () => replay(true));

    if (playIntro) replay(true);
    else showFull();
  </script>
</body>
</html>
"""

play_intro = not st.session_state.get("intro_played", False)
st.session_state.intro_played = True
robot_html = (
    ROBOT_HTML.replace("__INTRO_JSON__", json.dumps(INTRO_TEXT, ensure_ascii=False))
    .replace("__SPEECH_JSON__", json.dumps(SPEECH_TEXT, ensure_ascii=False))
    .replace("__PLAY_INTRO__", "true" if play_intro else "false")
)

hero_robot, hero_text = st.columns([1.25, 1], vertical_alignment="center", gap="small")
with hero_robot:
    st.iframe(robot_html, height=440)
with hero_text:
    st.markdown(
        """
        <div class="hero-title">AT</div>
        <div class="hero-kicker">Smart PDF Chatbot</div>
        <div class="hero-sub">ارفع ملف PDF واسأل AT. الإجابة تبقى مربوطة بنص الملف.</div>
        """,
        unsafe_allow_html=True,
    )

if not os.getenv("GROQ_API_KEY"):
    st.error("أضف GROQ_API_KEY في ملف .env ثم أعد تشغيل التطبيق.")
    st.stop()

pdfs = st.file_uploader(
    "ارفع ملف PDF أو أكثر",
    type=["pdf"],
    accept_multiple_files=True,
)

if not pdfs:
    st.info("ارفع ملفًا فيه نص قابل للتحديد. الملفات الممسوحة ضوئيًا بدون طبقة نص لن تُقرأ.")
    st.stop()

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

if store is None:
    st.error("لم يُستخرج نص من الملفات. تأكد أن الـ PDF يحتوي نصًا وليس صورًا فقط.")
    st.stop()

files_col, pages_col, chunks_col = st.columns(3)
files_col.metric("الملفات", stats["files"])
pages_col.metric("الصفحات", stats["pages"])
chunks_col.metric("المقاطع", stats["chunks"])

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "💬"):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources") or [])

question = st.chat_input("اكتب سؤالك هنا")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="💬"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            llm = load_llm(MODELS[model_label], effort)
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
            st.stop()

        answer = clean_answer(raw_answer)
        if not answer:
            answer = "لم تصل إجابة من النموذج. أعد المحاولة أو اختر عمق تفكير أقل."
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

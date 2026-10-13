import hashlib
import re
from io import BytesIO

import streamlit as st
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from atbot.constants import MODELS

ANSWER_PROMPT = ChatPromptTemplate.from_messages([(
    "human",
    "You are AT, a document assistant. Answer using only the context below.\n"
    "Rules:\n"
    "- Reply in the same language as the current question.\n"
    "- If the context does not contain the answer, say so in that language and do not guess.\n"
    "- Mention the file name and page number when that helps.\n"
    "- Do not add facts from outside the context.\n\n"
    "Context:\n{context}\n\n{input}",
)])

DOCUMENT_PROMPT = ChatPromptTemplate.from_template("File: {source} | Page: {page}\n{page_content}")
THINK_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL)


@st.cache_resource(show_spinner=False)
def load_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", encode_kwargs={"normalize_embeddings": True})


@st.cache_resource(show_spinner=False)
def load_llm(model_name: str):
    return ChatGroq(
        model=model_name,
        temperature=0.6,
        max_tokens=4096,
        reasoning_format="hidden",
        reasoning_effort="high",
        model_kwargs={"top_p": 0.95},
    )


def read_pdf(name: str, data: bytes):
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted and reader.decrypt("") == 0:
            return [], 0, f"{name} محمي بكلمة سر ولم يُفتح."
    except Exception:
        return [], 0, f"تعذّر فتح {name}. لو محمي بكلمة سر ارفع نسخة غير مشفرة."

    docs = []
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = (page.extract_text() or "").strip()
        except Exception:
            text = ""
        if text:
            docs.append(Document(page_content=text, metadata={"source": name, "page": number}))
    if not docs:
        return [], len(reader.pages), f"{name} مفيهوش نص قابل للقراءة (غالبًا صور فقط)."
    return docs, len(reader.pages), None


def build_index(files: dict):
    docs, pages, problems = [], 0, []
    for name, data in files.items():
        file_docs, file_pages, problem = read_pdf(name, data)
        docs += file_docs
        pages += file_pages
        if problem:
            problems.append(problem)

    if not docs:
        return None, pages, problems

    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
    return FAISS.from_documents(chunks, load_embeddings()), pages, problems


def file_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rebuild_index() -> None:
    st.session_state.index_error = None
    if not st.session_state.files:
        st.session_state.store = None
        st.session_state.pages = 0
        st.session_state.index_warnings = []
        return
    try:
        with st.spinner("بقرأ الملفات وبجهّز الفهرس… (أول مرة ممكن تاخد دقيقة)"):
            store, pages, problems = build_index(st.session_state.files)
    except Exception as error:
        st.session_state.store = None
        st.session_state.pages = 0
        st.session_state.index_error = str(error)
        st.error(f"تعذّر تجهيز الملفات: {error}")
        return

    st.session_state.store = store
    st.session_state.pages = pages
    st.session_state.index_warnings = problems
    for problem in problems:
        st.warning(problem)
    if store is None:
        st.session_state.index_error = "لم يُستخرج نص من الملفات. تأكّد أن الـ PDF فيه نص وليس صورًا فقط."
        st.error(st.session_state.index_error)
    else:
        st.success(f"تم — {len(st.session_state.files)} ملف، {pages} صفحة. اسأل عن المحتوى الآن.")


def ingest_uploads(uploaded) -> bool:
    if not uploaded:
        return False

    changed = False
    for file in uploaded:
        data = file.getvalue()
        digest = file_digest(data)
        if st.session_state.file_digests.get(file.name) != digest:
            st.session_state.files[file.name] = data
            st.session_state.file_digests[file.name] = digest
            changed = True

    if not changed:
        return False

    rebuild_index()
    return True


def remove_file(name: str) -> None:
    st.session_state.files.pop(name, None)
    st.session_state.file_digests.pop(name, None)
    rebuild_index()


def clear_all_files_and_chat() -> None:
    st.session_state.update(
        files={},
        file_digests={},
        store=None,
        pages=0,
        messages=[],
        index_error=None,
        index_warnings=[],
    )


def new_chat() -> None:
    st.session_state.messages = []
    st.session_state.pop("pending", None)


def recent_history(limit: int = 6) -> str:
    lines = []
    for message in st.session_state.messages[-limit:]:
        speaker = "User" if message["role"] == "user" else "AT"
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)


def render_sources(sources) -> None:
    if not sources:
        return
    with st.expander(f"المصادر · {len(sources)}"):
        for item in sources:
            st.markdown(
                f'<div class="source"><b>{item["source"]}</b> · صفحة {item["page"]}'
                f'<span>{item["snippet"]}</span></div>',
                unsafe_allow_html=True,
            )


def answer(question: str, model_label: str, k: int) -> None:
    history = recent_history()
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    reply = ""
    sources = []
    with st.chat_message("assistant"):
        if st.session_state.store is None:
            reply = (
                "Upload a PDF first using the upload area above or the attachment button in the chat input, "
                "then ask your question."
            )
            st.markdown(reply)
        else:
            docs = st.session_state.store.as_retriever(search_kwargs={"k": k}).invoke(question)
            composed = f"Previous conversation:\n{history}\n\nCurrent question: {question}" if history else question
            chain = create_stuff_documents_chain(
                load_llm(MODELS[model_label]), ANSWER_PROMPT, document_prompt=DOCUMENT_PROMPT
            )
            try:
                def stream_tokens():
                    for chunk in chain.stream({"input": composed, "context": docs}):
                        if isinstance(chunk, str):
                            yield chunk
                        elif hasattr(chunk, "content"):
                            text = chunk.content
                            if isinstance(text, str) and text:
                                yield text

                raw = st.write_stream(stream_tokens)
            except Exception as error:
                reply = f"حصلت مشكلة أثناء الرد: {error}"
                st.error(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply, "sources": []})
                return
            reply = THINK_PATTERN.sub("", raw or "").strip() or "مفيش رد وصل، جرّب تاني."
            sources = [
                {
                    "source": d.metadata.get("source", "PDF"),
                    "page": d.metadata.get("page", "—"),
                    "snippet": d.page_content[:240].replace("\n", " "),
                }
                for d in docs
            ]
            render_sources(sources)

    st.session_state.messages.append({"role": "assistant", "content": reply, "sources": sources})


def retry_last_turn() -> None:
    if len(st.session_state.messages) < 2:
        return
    if st.session_state.messages[-1]["role"] != "assistant":
        return
    user_msg = st.session_state.messages[-2]
    if user_msg["role"] != "user":
        return
    question = user_msg["content"]
    st.session_state.messages = st.session_state.messages[:-2]
    st.session_state.pending = question

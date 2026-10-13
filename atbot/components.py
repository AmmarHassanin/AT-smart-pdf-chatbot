import html
import json

import streamlit as st
import streamlit.components.v1 as components

from atbot.assets import robot_hero_html
from atbot.constants import MAX_UPLOAD_MB, MODELS, SUGGESTIONS
from atbot.core import (
    answer,
    clear_all_files_and_chat,
    ingest_uploads,
    new_chat,
    remove_file,
    render_sources,
    retry_last_turn,
)


def init_session(defaults: dict) -> None:
    for key, default in defaults.items():
        st.session_state.setdefault(key, default)


def fmt_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} GB"


def copy_to_clipboard_button(text: str, key: str) -> None:
    payload = json.dumps(text)
    components.html(
        f"""
        <button type="button" id="btn-{key}" style="
          font-family: Inter, sans-serif;
          font-size: 12px;
          font-weight: 500;
          padding: 6px 12px;
          border-radius: 8px;
          border: 1px solid #292F3A;
          background: #151922;
          color: #9CA3AF;
          cursor: pointer;
          transition: border-color 180ms ease, color 180ms ease;
        ">Copy</button>
        <script>
          const btn = document.getElementById("btn-{key}");
          btn.addEventListener("click", () => {{
            navigator.clipboard.writeText({payload}).then(() => {{
              btn.textContent = "Copied";
              btn.style.color = "#F5C451";
              btn.style.borderColor = "rgba(245,196,81,0.45)";
              setTimeout(() => {{
                btn.textContent = "Copy";
                btn.style.color = "#9CA3AF";
                btn.style.borderColor = "#292F3A";
              }}, 2000);
            }});
          }});
        </script>
        """,
        height=42,
    )


def render_footer() -> None:
    st.markdown(
        """
<div class="chat-footer-credit">
  <a class="dev-footer" href="https://ammarhassanin.github.io/portf0lio/" target="_blank" rel="noopener noreferrer">Developed by Ammar Yasser</a>
</div>
""",
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[str, int]:
    with st.sidebar:
        st.markdown(
            """
<div class="sidebar-brand">
  <div class="sidebar-brand__mark">🤖</div>
  <div class="sidebar-brand__text">AT <span>BOT</span></div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button("＋ New Chat", type="primary", use_container_width=True):
            new_chat()
            st.rerun()

        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        with st.expander("Settings"):
            model_label = st.selectbox("النموذج", list(MODELS))
            k = st.slider("عدد المقاطع المسترجعة", 2, 8, 4)
        st.markdown(
            '<p class="sidebar-footer-note">Theme: Dark (default)</p></div>',
            unsafe_allow_html=True,
        )

    return model_label, k


def _upload_zone_html() -> str:
    return f"""
<div class="upload-card">
  <div class="upload-card__head">
    <div class="upload-card__icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><polyline points="9 15 12 12 15 15"/></svg>
    </div>
    <p class="upload-card__title">Upload your PDF</p>
    <p class="upload-card__hint">Drag and drop your file here, or browse files</p>
    <p class="upload-card__limit">PDF only · up to {MAX_UPLOAD_MB}MB per file (Streamlit server limit)</p>
  </div>
</div>
"""


def render_file_list() -> None:
    if not st.session_state.files:
        return
    for name in list(st.session_state.files.keys()):
        data = st.session_state.files[name]
        safe_name = html.escape(name)
        st.markdown(
            f'<div class="file-chip"><div><div class="file-chip__name">{safe_name}</div>'
            f'<div class="file-chip__meta">{fmt_size(len(data))}</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Remove", key=f"remove_{name}", use_container_width=True):
            remove_file(name)
            st.rerun()
    if st.button("Clear chat & all files", use_container_width=True):
        clear_all_files_and_chat()
        st.rerun()


def render_welcome_hero() -> None:
    st.markdown('<div class="welcome-block">', unsafe_allow_html=True)
    hero = robot_hero_html()
    if hero:
        st.markdown(hero, unsafe_allow_html=True)
    else:
        st.warning("Robot image missing at assets/at-robot.jpg")
    st.markdown(
        """
<h1 class="welcome-title">Your AI Assistant</h1>
<p class="welcome-subtitle">Upload a document, ask questions, and discover insights instantly.</p>
""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_prompt_cards() -> None:
    if st.session_state.messages:
        return
    if st.session_state.store is None:
        st.markdown(
            '<p class="hub-hint">Upload a PDF above to enable suggested prompts.</p>',
            unsafe_allow_html=True,
        )
        return
    st.markdown('<p class="prompt-grid-label">Suggested prompts</p>', unsafe_allow_html=True)
    cols = st.columns(2)
    for idx, suggestion in enumerate(SUGGESTIONS):
        with cols[idx % 2]:
            if st.button(suggestion, key=f"sug_{idx}", use_container_width=True):
                st.session_state.pending = suggestion
                st.rerun()


def render_pdf_chat(model_label: str, k: int) -> None:
    has_chat = bool(st.session_state.messages)

    if not has_chat:
        render_welcome_hero()
    else:
        st.markdown(
            '<div class="page-header"><h1>Smart PDF Chat</h1>'
            "<p>Continue your conversation or upload more documents below.</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown(_upload_zone_html(), unsafe_allow_html=True)
    uploads = st.file_uploader(
        "PDF upload",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="main_pdf_uploader",
    )
    if uploads:
        ingest_uploads(uploads)

    render_file_list()

    if st.session_state.get("index_error") and not st.session_state.store:
        st.error(st.session_state.index_error)

    render_prompt_cards()

    question = st.session_state.pop("pending", None)

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                sources = message.get("sources")
                if sources:
                    render_sources(sources)
                st.markdown('<div class="msg-actions">', unsafe_allow_html=True)
                ac1, ac2, _ = st.columns([1, 1, 4])
                with ac1:
                    copy_to_clipboard_button(message["content"], f"copy_{idx}")
                with ac2:
                    if idx == len(st.session_state.messages) - 1:
                        if st.button("Retry", key=f"retry_{idx}"):
                            retry_last_turn()
                            st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    if question:
        answer(question, model_label, k)

    submission = st.chat_input(
        "Ask anything about your documents…",
        accept_file="multiple",
        file_type=["pdf"],
        key="pdf_chat_input",
    )
    if submission is not None:
        chat_files = getattr(submission, "files", None) or []
        if chat_files:
            ingest_uploads(chat_files)
        text = (getattr(submission, "text", "") or "").strip()
        if text:
            answer(text, model_label, k)



import html
import json

import streamlit as st
import streamlit.components.v1 as components

from atbot.assets import robot_hero_html
from atbot.chats import (
    active_chat,
    active_chat_id,
    delete_chat,
    ensure_chats,
    filter_chats,
    format_chat_timestamp,
    list_chats_newest_first,
    rename_chat,
    switch_chat,
)
from atbot.constants import MAX_UPLOAD_MB, MODELS
from atbot.doc_text import extract_text_from_files, primary_pdf
from atbot.icons import FEATURE_ICONS, ICON_ARROW, ICON_CHAT, ICON_INFO, ICON_UPLOAD_CLOUD, LOGO_SVG
from atbot.i18n import (
    get_lang,
    model_display,
    render_lang_switch_navbar,
    suggestions_for_lang,
    t,
)
from atbot.intelligence import prompt_for_task
from atbot.pdf_viewer import render_pdf_viewer
from atbot.translate import translate_document_text
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
    from atbot.persistence import _load_local_preferences

    _load_local_preferences()
    ensure_chats()


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
        <button type="button" id="btn-{key}" class="at-copy-btn">{html.escape(t("copy"))}</button>
        <script>
          const btn = document.getElementById("btn-{key}");
          btn.addEventListener("click", () => {{
            navigator.clipboard.writeText({payload}).then(() => {{
              btn.textContent = {json.dumps(t("copied"))};
              setTimeout(() => {{ btn.textContent = {json.dumps(t("copy"))}; }}, 2000);
            }});
          }});
        </script>
        """,
        height=38,
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


def render_navbar() -> None:
    with st.container(key="top_navbar"):
        render_lang_switch_navbar()


def _sidebar_brand() -> None:
    st.markdown(
        f"""
<div class="sidebar-brand">
  <div class="sidebar-brand__mark">{LOGO_SVG}</div>
  <div class="sidebar-brand__text">AT <span>PDF</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


def _sidebar_chat_row(chat: dict, current_id: str) -> None:
    cid = chat["id"]
    title = chat.get("title") or t("new_conversation")
    rename_id = st.session_state.get("rename_chat_id")
    pending_del = st.session_state.get("pending_delete_id")
    is_active = cid == current_id

    if pending_del == cid:
        st.warning(t("confirm_delete_title"))
        st.caption(t("confirm_delete_body"))
        dc1, dc2 = st.columns(2)
        with dc1:
            if st.button(t("confirm_yes"), key=f"confirm_del_yes_{cid}", type="primary", use_container_width=True):
                st.session_state.pending_delete_id = None
                delete_chat(cid)
                st.rerun()
        with dc2:
            if st.button(t("confirm_no"), key=f"confirm_del_no_{cid}", use_container_width=True):
                st.session_state.pending_delete_id = None
                st.rerun()
        return

    if rename_id == cid:
        new_title = st.text_input(t("rename_prompt"), value=title, key=f"rename_input_{cid}")
        if st.button(t("save_rename"), key=f"rename_save_{cid}", use_container_width=True):
            rename_chat(cid, new_title)
            st.session_state.rename_chat_id = None
            st.rerun()
        return

    time_label = format_chat_timestamp(chat.get("updated_at"))
    with st.container(key=f"chat_row_{cid}"):
        st.markdown(
            f"""
<div class="chat-card{' is-active' if is_active else ''}">
  <span class="chat-card__icon">{ICON_CHAT}</span>
  <div class="chat-card__body">
    <span class="chat-card__title">{html.escape(title)}</span>
    <span class="chat-card__time">{html.escape(time_label)}</span>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        with st.container(key=f"chat_switch_{cid}"):
            if st.button(title, key=f"open_chat_{cid}"):
                if not is_active:
                    switch_chat(cid)
                    st.rerun()
        with st.container(key=f"chat_actions_{cid}"):
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("​", key=f"rename_{cid}", help=t("rename_chat_help")):
                    st.session_state.rename_chat_id = cid
                    st.rerun()
            with ac2:
                if st.button("​", key=f"del_chat_{cid}", help=t("delete_chat_help")):
                    st.session_state.pending_delete_id = cid
                    st.rerun()


def render_sidebar() -> tuple[str, int]:
    with st.sidebar:
        with st.container(key="sidebar_top"):
            _sidebar_brand()
            with st.container(key="new_chat_wrap"):
                if st.button("+ " + t("new_chat"), type="primary", use_container_width=True):
                    new_chat()
                    st.rerun()

            with st.container(key="chat_search_wrap"):
                st.session_state.chat_search = st.text_input(
                    t("search_chats"),
                    value=st.session_state.get("chat_search", ""),
                    key="chat_search_input",
                    label_visibility="collapsed",
                    placeholder=t("search_chats"),
                )

        with st.container(key="sidebar_chat_list"):
            st.markdown(
                f'<div class="sidebar-section-label">{html.escape(t("conversations"))}</div>',
                unsafe_allow_html=True,
            )
            current_id = active_chat_id()
            chats = filter_chats(list_chats_newest_first(), st.session_state.get("chat_search", ""))
            if not chats:
                st.caption("—")
            for chat in chats:
                _sidebar_chat_row(chat, current_id)

        with st.container(key="sidebar_bottom"):
            with st.container(key="settings_wrap"):
                with st.expander(t("settings")):
                    model_label = st.selectbox(
                        t("model"),
                        list(MODELS.keys()),
                        format_func=model_display,
                    )
                    k = st.slider(t("chunks"), 2, 8, 4)
            st.markdown(
                f"""
<div class="sidebar-profile">
  <div class="sidebar-profile__avatar">A</div>
  <div class="sidebar-profile__meta">
    <span class="sidebar-profile__name">Ammar</span>
    <span class="sidebar-profile__plan">{html.escape(t("free_plan"))}</span>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

    return model_label, k


def _upload_zone_html() -> str:
    return f"""
<div class="upload-card">
  <div class="upload-card__head">
    <div class="upload-card__icon">{ICON_UPLOAD_CLOUD}</div>
    <p class="upload-card__title">{html.escape(t("upload_title"))}</p>
    <p class="upload-card__hint">{html.escape(t("upload_hint"))}</p>
    <p class="upload-card__limit">{ICON_INFO}{html.escape(t("upload_limit", mb=MAX_UPLOAD_MB))}</p>
  </div>
</div>
"""


def render_welcome_hero(chat: dict, cid: str) -> None:
    st.markdown('<div class="welcome-hero">', unsafe_allow_html=True)
    col_robot, col_text = st.columns([1, 1.2], gap="large")
    with col_robot:
        hero = robot_hero_html()
        if hero:
            st.markdown(hero, unsafe_allow_html=True)
    with col_text:
        title = t("welcome_title")
        lead, _, accent = title.partition(". ")
        accent = accent.rstrip(".")
        title_html = (
            f"{html.escape(lead)}.<span class=\"accent\">{html.escape(accent)}.</span>"
            if accent
            else html.escape(title)
        )
        st.markdown(
            f"""
<h1 class="welcome-title">{title_html}</h1>
<p class="welcome-subtitle">{html.escape(t("welcome_sub"))}</p>
""",
            unsafe_allow_html=True,
        )
        render_feature_cards(chat, cid)
    st.markdown("</div>", unsafe_allow_html=True)


def render_feature_cards(chat: dict, cid: str) -> None:
    items = [
        ("ask", t("feat_ask"), t("feat_ask_desc")),
        ("summary", t("feat_sum"), t("feat_sum_desc")),
        ("translate", t("feat_tr"), t("feat_tr_desc")),
        ("key_points", t("feat_keys"), t("feat_keys_desc")),
        ("explain", t("feat_explain"), t("feat_explain_desc")),
    ]
    st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, (task, title, desc) in enumerate(items):
        with cols[idx % 3]:
            with st.container(key=f"feature_card_{task}_{cid}"):
                st.markdown(
                    f"""
<div class="feature-card">
  <div class="feature-card__icon">{FEATURE_ICONS.get(task, ICON_CHAT)}</div>
  <p class="feature-card__title">{html.escape(title)}</p>
  <p class="feature-card__desc">{html.escape(desc)}</p>
  <span class="feature-card__arrow">{ICON_ARROW}</span>
</div>
""",
                    unsafe_allow_html=True,
                )
                if st.button(title, key=f"feat_{task}_{cid}"):
                    _run_feature(chat, task)
    st.markdown("</div>", unsafe_allow_html=True)


def _run_feature(chat: dict, task: str) -> None:
    if chat["store"] is None:
        st.warning(t("need_pdf"))
        return
    if task == "translate":
        st.session_state.show_translate_panel = True
        st.toast(t("feat_tr_desc"))
        st.rerun()
    elif task == "ask":
        st.toast(t("feat_ask_desc"))
    else:
        prompt = prompt_for_task(task)
        if prompt:
            chat["pending"] = prompt
            st.rerun()


def render_doc_status(chat: dict, *, compact: bool = False) -> None:
    if not chat["files"]:
        return
    names = ", ".join(html.escape(n) for n in list(chat["files"].keys())[:2])
    if len(chat["files"]) > 2:
        names += "…"
    if chat["store"]:
        meta = t("doc_pages", pages=chat["pages"], files=len(chat["files"]))
        st.markdown(
            f'<div class="doc-status doc-status--ready"><strong>{html.escape(t("doc_ready"))}</strong> · '
            f"{names}<br><span>{html.escape(meta)}</span></div>",
            unsafe_allow_html=True,
        )
    elif chat.get("index_error") and not compact:
        st.error(chat["index_error"])
    else:
        st.markdown(
            f'<div class="doc-status"><strong>{names}</strong><br>{html.escape(t("doc_no_index"))}</div>',
            unsafe_allow_html=True,
        )


def render_pdf_center_column(chat: dict, cid: str) -> None:
    primary = primary_pdf(chat["files"])
    if not primary:
        return
    name, data = primary
    page_key = f"pdf_page_{cid}"
    zoom_key = f"pdf_zoom_{cid}"
    st.session_state.setdefault(page_key, 1)
    st.session_state.setdefault(zoom_key, 1.0)

    r1, r2, r3 = st.columns([1, 1, 2])
    with r1:
        if st.button(t("remove_file"), key=f"ws_remove_{cid}", use_container_width=True):
            remove_file(name)
            st.rerun()
    with r2:
        replacement = st.file_uploader(
            t("replace_file"),
            type=["pdf"],
            key=f"replace_pdf_{cid}",
            label_visibility="collapsed",
        )
        if replacement is not None:
            remove_file(name)
            ingest_uploads([replacement])
            st.rerun()

    meta = f"{fmt_size(len(data))} · {t('doc_pages', pages=chat.get('pages') or '—', files=len(chat['files']))}"
    render_pdf_viewer(
        data,
        filename=name,
        meta_line=meta,
        page=st.session_state[page_key],
        zoom=st.session_state[zoom_key],
        element_id=f"pdf_{cid}",
    )


def _ai_panel_header() -> None:
    st.markdown(
        f"""
<div class="at-ai-panel__head">
  <div class="at-ai-panel__avatar">AT</div>
  <div>
    <p class="at-ai-panel__title">{html.escape(t("panel_assistant"))}</p>
    <p class="at-ai-panel__sub">{html.escape(t("chat_sub"))}</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_tool_tab(chat: dict, task: str, model_label: str, cid: str) -> None:
    if task == "translate":
        _render_translate_tab(chat, model_label, cid)
        return
    if chat["store"] is None:
        st.info(t("need_pdf"))
        return
    st.caption(prompt_for_task(task) or "")
    if st.button(t("run_action"), key=f"tab_run_{task}_{cid}", type="primary", use_container_width=True):
        prompt = prompt_for_task(task)
        if prompt:
            chat["pending"] = prompt
            st.rerun()


def _render_translate_direction_toggle(cid: str) -> tuple[str, str]:
    """Horizontal EN ↔ AR target picker; source stays auto-detect."""
    default_tgt = "ar" if get_lang() == "en" else "en"
    seg_key = f"tr_dir_{cid}"
    st.markdown(
        f'<p class="tr-dir-label">{html.escape(t("translate_target"))}</p>',
        unsafe_allow_html=True,
    )
    with st.container(key="tr_dir_toggle"):
        tgt = st.segmented_control(
            t("translate_target"),
            options=["en", "ar"],
            default=st.session_state.get(seg_key, default_tgt),
            format_func=lambda x: t(f"translate_{x}"),
            key=seg_key,
            label_visibility="collapsed",
        )
    return "auto", tgt or default_tgt


def _render_translate_tab(chat: dict, model_label: str, cid: str) -> None:
    if not chat["files"]:
        st.info(t("need_pdf"))
        return
    src, tgt = _render_translate_direction_toggle(cid)
    if st.button(t("translate_run"), key=f"tr_run_tab_{cid}", type="primary", use_container_width=True):
        text = extract_text_from_files(chat["files"])
        if not text:
            st.warning(t("translate_empty"))
        else:
            with st.spinner(t("processing")):
                out, engine = translate_document_text(
                    text, src, tgt, model_name=MODELS[model_label]
                )
            if out:
                st.session_state[f"translate_out_{cid}"] = out
                st.session_state[f"translate_engine_{cid}"] = engine
    stored = st.session_state.get(f"translate_out_{cid}")
    if stored:
        eng = st.session_state.get(f"translate_engine_{cid}", "")
        st.markdown(f"**{t('translate_result')}** ({eng})")
        st.markdown(stored)


def _render_chat_history(chat: dict, cid: str) -> None:
    if not chat["messages"]:
        return
    with st.container(key="chat_scroll_area"):
        for idx, message in enumerate(chat["messages"]):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    sources = message.get("sources")
                    if sources:
                        render_sources(sources)
                    ac1, ac2, _ = st.columns([1, 1, 3])
                    with ac1:
                        copy_to_clipboard_button(message["content"], f"copy_{cid}_{idx}")
                    with ac2:
                        if idx == len(chat["messages"]) - 1:
                            if st.button(t("retry"), key=f"retry_{cid}_{idx}"):
                                retry_last_turn()
                                st.rerun()


AI_MODES = (
    ("chat", "tab_chat"),
    ("summary", "tab_summary"),
    ("translate", "tab_translate"),
    ("key_points", "tab_key_points"),
    ("explain", "tab_explain"),
)


def render_ai_panel(chat: dict, model_label: str, cid: str) -> None:
    _ai_panel_header()
    mode_key = f"ai_mode_{cid}"
    st.session_state.setdefault(mode_key, "chat")
    active_mode = st.session_state[mode_key]

    with st.container(key="ai_toolbar"):
        cols = st.columns(len(AI_MODES))
        for col, (mode, label_key) in zip(cols, AI_MODES):
            with col:
                if st.button(
                    t(label_key),
                    key=f"mode_{mode}_{cid}",
                    type="primary" if active_mode == mode else "secondary",
                    use_container_width=True,
                ):
                    st.session_state[mode_key] = mode
                    st.rerun()

    if active_mode == "chat":
        _render_chat_history(chat, cid)
        st.markdown('<div class="at-composer">', unsafe_allow_html=True)
        draft = st.text_area(
            t("chat_input"),
            key=f"panel_chat_{cid}",
            height=88,
            label_visibility="collapsed",
            placeholder=t("chat_input"),
        )
        if st.button(t("send"), key=f"panel_send_{cid}", type="primary", use_container_width=True):
            text = (draft or "").strip()
            if text:
                chat["pending"] = text
                st.session_state.pop(f"panel_chat_{cid}", None)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    elif active_mode == "translate":
        _render_translate_tab(chat, model_label, cid)
    else:
        _render_tool_tab(chat, active_mode, model_label, cid)


def _render_upload_block(cid: str) -> None:
    with st.container(key="upload_dropzone"):
        st.markdown(_upload_zone_html(), unsafe_allow_html=True)
        uploads = st.file_uploader(
            "PDF upload",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"main_pdf_uploader_{cid}",
        )
    if uploads:
        ingest_uploads(uploads)


def render_pdf_chat(model_label: str, k: int) -> None:
    chat = active_chat()
    cid = active_chat_id()
    workspace = bool(chat["files"])
    has_chat = bool(chat["messages"])
    if not workspace:
        if not has_chat:
            render_welcome_hero(chat, cid)
        else:
            render_feature_cards(chat, cid)
        _render_upload_block(cid)
        render_doc_status(chat)
        if chat.get("index_error") and chat["files"]:
            st.error(chat["index_error"])
        if chat["store"] and not chat["messages"]:
            st.markdown(
                f'<p class="prompt-grid-label">{html.escape(t("prompts_label"))}</p>',
                unsafe_allow_html=True,
            )
            cols = st.columns(2)
            for idx, suggestion in enumerate(suggestions_for_lang()):
                with cols[idx % 2]:
                    if st.button(suggestion, key=f"sug_{cid}_{idx}", use_container_width=True):
                        chat["pending"] = suggestion
                        st.rerun()
        _render_chat_history(chat, cid)
        question = chat.pop("pending", None)
        if question:
            answer(question, model_label, k)
        submission = st.chat_input(
            t("chat_input"),
            accept_file="multiple",
            file_type=["pdf"],
            key=f"pdf_chat_input_{cid}",
        )
        if submission is not None:
            chat_files = getattr(submission, "files", None) or []
            if chat_files:
                ingest_uploads(chat_files)
            text = (getattr(submission, "text", "") or "").strip()
            if text:
                answer(text, model_label, k)
        return

    st.markdown('<span class="at-workspace-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    render_doc_status(chat, compact=True)

    col_pdf, col_ai = st.columns([3, 2], gap="large")
    with col_pdf:
        with st.container(key="workspace_pdf_panel"):
            render_pdf_center_column(chat, cid)
    with col_ai:
        with st.container(key="workspace_ai_panel"):
            render_ai_panel(chat, model_label, cid)

    if chat.get("index_error") and not chat["store"]:
        st.error(chat["index_error"])

    question = chat.pop("pending", None)
    if question:
        answer(question, model_label, k)

    submission = st.chat_input(
        t("chat_input"),
        accept_file="multiple",
        file_type=["pdf"],
        key=f"pdf_chat_input_ws_{cid}",
    )
    if submission is not None:
        chat_files = getattr(submission, "files", None) or []
        if chat_files:
            ingest_uploads(chat_files)
        text = (getattr(submission, "text", "") or "").strip()
        if text:
            answer(text, model_label, k)

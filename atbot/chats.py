import uuid
from datetime import datetime, timezone

import streamlit as st

from atbot.env import is_production
from atbot.identity import resolve_user_id

CHAT_KEYS = (
    "messages",
    "files",
    "file_digests",
    "store",
    "pages",
    "index_error",
    "index_warnings",
    "pending",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def format_chat_timestamp(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local = dt.astimezone()
    now = datetime.now(local.tzinfo)
    time_part = local.strftime("%I:%M %p").lstrip("0")
    if local.date() == now.date():
        return f"Today, {time_part}"
    yesterday = now.date().toordinal() - 1
    if local.date().toordinal() == yesterday:
        return f"Yesterday, {time_part}"
    return f"{local.strftime('%b')} {local.day}, {local.year}"


def _empty_chat(chat_id: str | None = None, title: str = "محادثة جديدة") -> dict:
    return {
        "id": chat_id or uuid.uuid4().hex[:10],
        "title": title,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "messages": [],
        "files": {},
        "file_digests": {},
        "store": None,
        "pages": 0,
        "index_error": None,
        "index_warnings": [],
        "pending": None,
    }


def _legacy_flat_state() -> dict | None:
    if not st.session_state.get("messages") and not st.session_state.get("files"):
        return None
    chat = _empty_chat(title="محادثة 1")
    for key in CHAT_KEYS:
        if key in st.session_state:
            chat[key] = st.session_state[key]
    if chat["messages"]:
        first = next((m["content"] for m in chat["messages"] if m["role"] == "user"), None)
        if first:
            chat["title"] = _title_from_text(first)
    return chat


def _ensure_chats_local() -> None:
    if st.session_state.get("chats") and st.session_state.get("active_chat_id"):
        if st.session_state.active_chat_id in st.session_state.chats:
            return

    legacy = _legacy_flat_state()
    if legacy:
        cid = legacy["id"]
        st.session_state.chats = {cid: legacy}
        st.session_state.active_chat_id = cid
    else:
        chat = _empty_chat()
        st.session_state.chats = {chat["id"]: chat}
        st.session_state.active_chat_id = chat["id"]

    for key in CHAT_KEYS:
        st.session_state.pop(key, None)


def _ensure_chats_production() -> None:
    from atbot.persistence import hydrate_chat_files, load_user_state, persist_user_state

    user_id = resolve_user_id()
    if st.session_state.get("_chat_user") != user_id:
        st.session_state._chat_user = user_id
        st.session_state._chats_hydrated = False
        st.session_state.chats = {}
        st.session_state.active_chat_id = None

    if not st.session_state.get("_chats_hydrated"):
        disk_chats, disk_active = load_user_state()
        if disk_chats:
            st.session_state.chats = disk_chats
            if disk_active and disk_active in disk_chats:
                st.session_state.active_chat_id = disk_active
            else:
                st.session_state.active_chat_id = next(iter(disk_chats))
        else:
            chat = _empty_chat()
            st.session_state.chats = {chat["id"]: chat}
            st.session_state.active_chat_id = chat["id"]

        active = st.session_state.chats[st.session_state.active_chat_id]
        hydrate_chat_files(active, user_id)
        st.session_state._chats_hydrated = True
        from atbot.core import rebuild_index

        rebuild_index(quiet=True)
        persist_user_state()

    for key in CHAT_KEYS:
        st.session_state.pop(key, None)


def ensure_chats() -> None:
    if is_production():
        _ensure_chats_production()
    else:
        _ensure_chats_local()


def active_chat() -> dict:
    ensure_chats()
    return st.session_state.chats[st.session_state.active_chat_id]


def active_chat_id() -> str:
    ensure_chats()
    return st.session_state.active_chat_id


def list_chats_newest_first() -> list[dict]:
    ensure_chats()
    chats = list(st.session_state.chats.values())
    chats.sort(key=lambda c: c.get("updated_at", ""), reverse=True)
    return chats


def _title_from_text(text: str, max_len: int = 36) -> str:
    line = " ".join(text.strip().split())
    if len(line) <= max_len:
        return line or "محادثة جديدة"
    return line[: max_len - 1] + "…"


def touch_chat(chat: dict) -> None:
    chat["updated_at"] = _now_iso()


def create_new_chat() -> str:
    from atbot.persistence import persist_user_state

    ensure_chats()
    chat = _empty_chat()
    st.session_state.chats[chat["id"]] = chat
    st.session_state.active_chat_id = chat["id"]
    persist_user_state()
    return chat["id"]


def switch_chat(chat_id: str) -> None:
    from atbot.persistence import hydrate_chat_files, persist_user_state

    ensure_chats()
    if chat_id not in st.session_state.chats:
        return
    if chat_id == st.session_state.active_chat_id:
        return

    persist_user_state()
    st.session_state.active_chat_id = chat_id

    if is_production():
        chat = active_chat()
        hydrate_chat_files(chat)
        from atbot.core import rebuild_index

        rebuild_index(quiet=True)
    persist_user_state()


def delete_chat(chat_id: str) -> None:
    from atbot.persistence import delete_chat_storage, hydrate_chat_files, persist_user_state

    ensure_chats()
    user_id = resolve_user_id() if is_production() else None

    if len(st.session_state.chats) <= 1:
        if is_production() and user_id:
            delete_chat_storage(user_id, chat_id)
        st.session_state.chats = {}
        st.session_state.active_chat_id = None
        create_new_chat()
        return

    st.session_state.chats.pop(chat_id, None)
    if is_production() and user_id:
        delete_chat_storage(user_id, chat_id)

    if st.session_state.active_chat_id == chat_id:
        st.session_state.active_chat_id = next(iter(st.session_state.chats))
        if is_production():
            hydrate_chat_files(active_chat(), user_id)
            from atbot.core import rebuild_index

            rebuild_index(quiet=True)

    persist_user_state()


def maybe_set_title_from_question(question: str) -> None:
    chat = active_chat()
    if chat["title"] == "محادثة جديدة" or not chat["title"].strip():
        chat["title"] = _title_from_text(question)


def rename_chat(chat_id: str, new_title: str) -> None:
    from atbot.persistence import persist_user_state

    ensure_chats()
    title = " ".join((new_title or "").strip().split())
    if not title or chat_id not in st.session_state.chats:
        return
    st.session_state.chats[chat_id]["title"] = _title_from_text(title, max_len=48)
    touch_chat(st.session_state.chats[chat_id])
    persist_user_state()


def filter_chats(chats: list[dict], query: str) -> list[dict]:
    q = " ".join((query or "").strip().lower().split())
    if not q:
        return chats
    out = []
    for chat in chats:
        title = (chat.get("title") or "").lower()
        if q in title:
            out.append(chat)
            continue
        for msg in chat.get("messages") or []:
            if q in (msg.get("content") or "").lower():
                out.append(chat)
                break
    return out

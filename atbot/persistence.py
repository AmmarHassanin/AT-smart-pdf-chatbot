import json
import re
import shutil
from pathlib import Path

import streamlit as st

from atbot.env import is_production
from atbot.identity import resolve_user_id

DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "users"

CHAT_META_KEYS = (
    "id",
    "title",
    "created_at",
    "updated_at",
    "messages",
    "pages",
    "index_error",
    "index_warnings",
    "file_digests",
)


def _safe_user_id(user_id: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", user_id)
    return cleaned[:64] or "anonymous"


def user_root(user_id: str | None = None) -> Path:
    uid = _safe_user_id(user_id or resolve_user_id())
    return DATA_ROOT / uid


def _meta_path(user_id: str) -> Path:
    return user_root(user_id) / "chats_meta.json"


def _chat_files_dir(user_id: str, chat_id: str) -> Path:
    safe_chat = re.sub(r"[^a-zA-Z0-9_-]", "", chat_id)[:32]
    return user_root(user_id) / "chats" / safe_chat / "files"


def chat_to_meta(chat: dict) -> dict:
    meta = {key: chat.get(key) for key in CHAT_META_KEYS}
    meta["id"] = chat["id"]
    return meta


def meta_to_chat(meta: dict) -> dict:
    chat = {
        "id": meta["id"],
        "title": meta.get("title") or "محادثة جديدة",
        "created_at": meta.get("created_at"),
        "updated_at": meta.get("updated_at"),
        "messages": meta.get("messages") or [],
        "files": {},
        "file_digests": meta.get("file_digests") or {},
        "store": None,
        "pages": meta.get("pages") or 0,
        "index_error": meta.get("index_error"),
        "index_warnings": meta.get("index_warnings") or [],
        "pending": None,
    }
    return chat


def save_chat_files(user_id: str, chat: dict) -> None:
    folder = _chat_files_dir(user_id, chat["id"])
    folder.mkdir(parents=True, exist_ok=True)
    for name, data in chat.get("files", {}).items():
        safe_name = Path(name).name
        (folder / safe_name).write_bytes(data)
    # Remove PDFs no longer in this chat
    keep = {Path(n).name for n in chat.get("files", {})}
    for path in folder.glob("*"):
        if path.is_file() and path.name not in keep:
            path.unlink(missing_ok=True)


def load_chat_files(user_id: str, chat_id: str) -> dict[str, bytes]:
    folder = _chat_files_dir(user_id, chat_id)
    if not folder.is_dir():
        return {}
    files: dict[str, bytes] = {}
    for path in folder.glob("*"):
        if path.is_file():
            files[path.name] = path.read_bytes()
    return files


def delete_chat_storage(user_id: str, chat_id: str) -> None:
    safe_chat = re.sub(r"[^a-zA-Z0-9_-]", "", chat_id)[:32]
    chat_dir = user_root(user_id) / "chats" / safe_chat
    if chat_dir.is_dir():
        shutil.rmtree(chat_dir, ignore_errors=True)


def persist_user_state() -> None:
    if not is_production():
        return
    user_id = resolve_user_id()
    chats = st.session_state.get("chats") or {}
    active = st.session_state.get("active_chat_id")
    root = user_root(user_id)
    root.mkdir(parents=True, exist_ok=True)

    for chat in chats.values():
        save_chat_files(user_id, chat)

    payload = {
        "active_chat_id": active,
        "chats": {cid: chat_to_meta(c) for cid, c in chats.items()},
    }
    _meta_path(user_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_user_state() -> tuple[dict[str, dict], str | None]:
    user_id = resolve_user_id()
    path = _meta_path(user_id)
    if not path.is_file():
        return {}, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}, None
    chats = {cid: meta_to_chat(meta) for cid, meta in (payload.get("chats") or {}).items()}
    return chats, payload.get("active_chat_id")


def hydrate_chat_files(chat: dict, user_id: str | None = None) -> None:
    uid = user_id or resolve_user_id()
    chat["files"] = load_chat_files(uid, chat["id"])
    chat["store"] = None

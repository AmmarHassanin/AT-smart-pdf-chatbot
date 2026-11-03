"""Per-user chat persistence (disk) + in-memory FAISS index cache. No Streamlit deps."""

from __future__ import annotations

import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from .pdf import build_index, file_digest

DATA_ROOT = Path(__file__).resolve().parent.parent.parent / "data" / "users"

_lock = Lock()
_index_cache: dict[str, object] = {}  # f"{uid}:{chat_id}" -> FAISS store


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_id(value: str, max_len: int = 64) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", value or "")
    return cleaned[:max_len] or "anonymous"


def _user_root(uid: str) -> Path:
    return DATA_ROOT / _safe_id(uid)


def _meta_path(uid: str) -> Path:
    return _user_root(uid) / "chats_meta.json"


def _chat_files_dir(uid: str, chat_id: str) -> Path:
    return _user_root(uid) / "chats" / _safe_id(chat_id, 32) / "files"


def _empty_chat() -> dict:
    now = _now_iso()
    return {
        "id": uuid.uuid4().hex[:10],
        "title": "New chat",
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "file_digests": {},
        "pages": 0,
        "index_warnings": [],
    }


def _load_all(uid: str) -> dict:
    path = _meta_path(uid)
    if not path.is_file():
        return {"active_chat_id": None, "chats": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"active_chat_id": None, "chats": {}}


def _save_all(uid: str, payload: dict) -> None:
    root = _user_root(uid)
    root.mkdir(parents=True, exist_ok=True)
    _meta_path(uid).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def list_chats(uid: str) -> list[dict]:
    payload = _load_all(uid)
    chats = list(payload.get("chats", {}).values())
    chats.sort(key=lambda c: c.get("updated_at", ""), reverse=True)
    return chats


def get_chat(uid: str, chat_id: str) -> dict | None:
    payload = _load_all(uid)
    return payload.get("chats", {}).get(chat_id)


def create_chat(uid: str) -> dict:
    with _lock:
        payload = _load_all(uid)
        chat = _empty_chat()
        payload.setdefault("chats", {})[chat["id"]] = chat
        payload["active_chat_id"] = chat["id"]
        _save_all(uid, payload)
        return chat


def rename_chat(uid: str, chat_id: str, title: str) -> dict | None:
    title = " ".join((title or "").strip().split())
    if not title:
        return None
    with _lock:
        payload = _load_all(uid)
        chat = payload.get("chats", {}).get(chat_id)
        if not chat:
            return None
        chat["title"] = title[:48]
        chat["updated_at"] = _now_iso()
        _save_all(uid, payload)
        return chat


def delete_chat(uid: str, chat_id: str) -> None:
    with _lock:
        payload = _load_all(uid)
        payload.get("chats", {}).pop(chat_id, None)
        _save_all(uid, payload)
    chat_dir = _chat_files_dir(uid, chat_id).parent
    if chat_dir.is_dir():
        shutil.rmtree(chat_dir, ignore_errors=True)
    _index_cache.pop(f"{uid}:{chat_id}", None)


def touch_chat(uid: str, chat_id: str, *, title_from: str | None = None) -> None:
    with _lock:
        payload = _load_all(uid)
        chat = payload.get("chats", {}).get(chat_id)
        if not chat:
            return
        chat["updated_at"] = _now_iso()
        if title_from and (not chat.get("title") or chat["title"] == "New chat"):
            line = " ".join(title_from.strip().split())
            chat["title"] = (line[:35] + "…") if len(line) > 36 else (line or "New chat")
        _save_all(uid, payload)


def append_message(uid: str, chat_id: str, role: str, content: str, sources: list[dict] | None = None) -> None:
    with _lock:
        payload = _load_all(uid)
        chat = payload.get("chats", {}).get(chat_id)
        if not chat:
            return
        chat["messages"].append({"role": role, "content": content, "sources": sources or []})
        chat["updated_at"] = _now_iso()
        _save_all(uid, payload)


def load_files(uid: str, chat_id: str) -> dict[str, bytes]:
    folder = _chat_files_dir(uid, chat_id)
    if not folder.is_dir():
        return {}
    return {p.name: p.read_bytes() for p in folder.glob("*") if p.is_file()}


def save_uploaded_files(uid: str, chat_id: str, files: dict[str, bytes]) -> tuple[bool, list[dict]]:
    """Writes new/changed files to disk, rebuilds the index, updates meta. Returns (changed, warnings)."""
    folder = _chat_files_dir(uid, chat_id)
    folder.mkdir(parents=True, exist_ok=True)

    with _lock:
        payload = _load_all(uid)
        chat = payload.get("chats", {}).get(chat_id)
        if not chat:
            return False, []
        digests = chat.setdefault("file_digests", {})
        changed = False
        for name, data in files.items():
            digest = file_digest(data)
            if digests.get(name) != digest:
                (folder / Path(name).name).write_bytes(data)
                digests[name] = digest
                changed = True
        if not changed:
            return False, []
        _save_all(uid, payload)

    all_files = load_files(uid, chat_id)
    store, pages, warnings = build_index(all_files)
    _index_cache[f"{uid}:{chat_id}"] = store

    with _lock:
        payload = _load_all(uid)
        chat = payload.get("chats", {}).get(chat_id)
        if chat:
            chat["pages"] = pages
            chat["index_warnings"] = warnings
            chat["updated_at"] = _now_iso()
            _save_all(uid, payload)
    return True, warnings


def remove_file(uid: str, chat_id: str, filename: str) -> None:
    folder = _chat_files_dir(uid, chat_id)
    target = folder / Path(filename).name
    target.unlink(missing_ok=True)

    with _lock:
        payload = _load_all(uid)
        chat = payload.get("chats", {}).get(chat_id)
        if chat:
            chat.get("file_digests", {}).pop(filename, None)
            _save_all(uid, payload)

    all_files = load_files(uid, chat_id)
    if all_files:
        store, pages, warnings = build_index(all_files)
    else:
        store, pages, warnings = None, 0, []
    _index_cache[f"{uid}:{chat_id}"] = store

    with _lock:
        payload = _load_all(uid)
        chat = payload.get("chats", {}).get(chat_id)
        if chat:
            chat["pages"] = pages
            chat["index_warnings"] = warnings
            _save_all(uid, payload)


def get_index(uid: str, chat_id: str):
    """Returns the cached FAISS store, rebuilding from disk if the process restarted."""
    key = f"{uid}:{chat_id}"
    if key in _index_cache:
        return _index_cache[key]
    files = load_files(uid, chat_id)
    if not files:
        _index_cache[key] = None
        return None
    store, _pages, _warnings = build_index(files)
    _index_cache[key] = store
    return store

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from ..core import store
from ..core.constants import MAX_UPLOAD_MB, MODELS, TASK_PROMPTS
from ..core.doc_text import extract_text_from_files
from ..core.rag import clean_reply, docs_to_sources, stream_answer
from ..core.translate import translate_document_text
from .deps import resolve_user_id

router = APIRouter(prefix="/api", tags=["chats"])


class RenameBody(BaseModel):
    title: str


class AskBody(BaseModel):
    question: str
    model: str = "accurate"
    k: int = 4


class TranslateBody(BaseModel):
    source: str = "auto"
    target: str = "en"
    model: str = "accurate"


def _recent_history(chat: dict, limit: int = 6) -> str:
    lines = []
    for message in chat["messages"][-limit:]:
        speaker = "User" if message["role"] == "user" else "AT"
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)


@router.get("/chats")
def list_chats(uid: str = Depends(resolve_user_id)):
    return store.list_chats(uid)


@router.post("/chats")
def create_chat(uid: str = Depends(resolve_user_id)):
    return store.create_chat(uid)


@router.get("/chats/{chat_id}")
def get_chat(chat_id: str, uid: str = Depends(resolve_user_id)):
    chat = store.get_chat(uid, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")
    return chat


@router.patch("/chats/{chat_id}")
def rename_chat(chat_id: str, body: RenameBody, uid: str = Depends(resolve_user_id)):
    chat = store.rename_chat(uid, chat_id, body.title)
    if not chat:
        raise HTTPException(404, "Chat not found")
    return chat


@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: str, uid: str = Depends(resolve_user_id)):
    store.delete_chat(uid, chat_id)
    return {"ok": True}


@router.post("/chats/{chat_id}/files")
async def upload_files(chat_id: str, files: list[UploadFile] = File(...), uid: str = Depends(resolve_user_id)):
    if not store.get_chat(uid, chat_id):
        raise HTTPException(404, "Chat not found")
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    payload: dict[str, bytes] = {}
    for f in files:
        data = await f.read()
        if len(data) > max_bytes:
            raise HTTPException(413, f"{f.filename} exceeds the {MAX_UPLOAD_MB}MB limit.")
        payload[f.filename] = data
    changed, warnings = store.save_uploaded_files(uid, chat_id, payload)
    chat = store.get_chat(uid, chat_id)
    return {"changed": changed, "warnings": warnings, "pages": chat.get("pages", 0) if chat else 0}


@router.delete("/chats/{chat_id}/files/{filename}")
def delete_file(chat_id: str, filename: str, uid: str = Depends(resolve_user_id)):
    store.remove_file(uid, chat_id, filename)
    return {"ok": True}


@router.get("/chats/{chat_id}/files/{filename}")
def get_file(chat_id: str, filename: str, uid: str = Depends(resolve_user_id)):
    files = store.load_files(uid, chat_id)
    data = files.get(filename)
    if data is None:
        raise HTTPException(404, "File not found")
    return Response(content=data, media_type="application/pdf")


@router.post("/chats/{chat_id}/ask")
async def ask(chat_id: str, body: AskBody, uid: str = Depends(resolve_user_id)):
    chat = store.get_chat(uid, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")
    model_name = MODELS.get(body.model, MODELS["accurate"])
    index = store.get_index(uid, chat_id)

    store.append_message(uid, chat_id, "user", body.question)
    store.touch_chat(uid, chat_id, title_from=body.question)

    if index is None:
        async def empty_gen():
            yield {"event": "token", "data": ""}
            yield {"event": "done", "data": json.dumps({"reply": "", "sources": [], "error": "no_index"})}

        return EventSourceResponse(empty_gen())

    history = _recent_history(chat)
    docs = index.as_retriever(search_kwargs={"k": body.k}).invoke(body.question)

    async def event_gen():
        collected = []
        try:
            for chunk in stream_answer(body.question, history, docs, model_name):
                collected.append(chunk)
                yield {"event": "token", "data": chunk}
        except Exception as error:
            yield {"event": "error", "data": str(error)}
            return
        reply = clean_reply("".join(collected)) or ""
        sources = docs_to_sources(docs)
        store.append_message(uid, chat_id, "assistant", reply, sources)
        yield {"event": "done", "data": json.dumps({"reply": reply, "sources": sources})}

    return EventSourceResponse(event_gen())


@router.post("/chats/{chat_id}/translate")
def translate(chat_id: str, body: TranslateBody, uid: str = Depends(resolve_user_id)):
    files = store.load_files(uid, chat_id)
    if not files:
        raise HTTPException(400, "No files uploaded for this chat")
    text = extract_text_from_files(files)
    if not text:
        return {"text": "", "engine": "none"}
    model_name = MODELS.get(body.model, MODELS["accurate"])
    out, engine, error = translate_document_text(text, body.source, body.target, model_name=model_name)
    if error:
        raise HTTPException(500, error)
    return {"text": out, "engine": engine}


@router.get("/tasks/{task}")
def task_prompt(task: str):
    prompt = TASK_PROMPTS.get(task)
    if not prompt:
        raise HTTPException(404, "Unknown task")
    return {"prompt": prompt}

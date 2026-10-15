"""Document translation (Arabic ↔ English) with safe fallbacks."""

from __future__ import annotations

import re

import streamlit as st

CHUNK_SIZE = 4500


def _split_chunks(text: str) -> list[str]:
    text = text.strip()
    if len(text) <= CHUNK_SIZE:
        return [text]
    parts: list[str] = []
    cursor = 0
    while cursor < len(text):
        end = min(cursor + CHUNK_SIZE, len(text))
        if end < len(text):
            split = text.rfind("\n", cursor, end)
            if split > cursor + 500:
                end = split
        parts.append(text[cursor:end].strip())
        cursor = end
    return [p for p in parts if p]


def _map_lang(code: str) -> str:
    if code in ("ar", "arabic"):
        return "ar"
    if code in ("en", "english"):
        return "en"
    return code


def translate_with_deep_translator(text: str, source: str, target: str) -> str:
    from deep_translator import GoogleTranslator

    src = "auto" if source == "auto" else _map_lang(source)
    tgt = _map_lang(target)
    out: list[str] = []
    for chunk in _split_chunks(text):
        translator = GoogleTranslator(source=src, target=tgt)
        out.append(translator.translate(chunk))
        src = tgt
    return "\n\n".join(out).strip()


def translate_with_groq(text: str, source: str, target: str, model_name: str) -> str:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_groq import ChatGroq

    lang_label = {"ar": "Arabic", "en": "English"}.get(_map_lang(target), target)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "Translate the following document excerpt into {lang}. "
                "Preserve meaning and paragraph breaks. Output only the translation.\n\n{text}",
            )
        ]
    )
    llm = ChatGroq(model=model_name, temperature=0.2, max_tokens=4096, reasoning_format="hidden")
    out: list[str] = []
    for chunk in _split_chunks(text):
        msg = prompt.invoke({"lang": lang_label, "text": chunk})
        response = llm.invoke(msg)
        content = getattr(response, "content", "") or str(response)
        out.append(re.sub(r"</?redacted_thinking>.*", "", content, flags=re.DOTALL).strip())
    return "\n\n".join(out).strip()


def translate_document_text(
    text: str,
    source: str,
    target: str,
    *,
    model_name: str,
) -> tuple[str, str]:
    """Returns (translated_text, engine_label)."""
    if not text.strip():
        return "", "none"
    try:
        return translate_with_deep_translator(text, source, target), "google"
    except Exception:
        try:
            return translate_with_groq(text, source, target, model_name), "groq"
        except Exception as error:
            st.error(str(error))
            return "", "error"

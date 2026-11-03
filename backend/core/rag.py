"""Groq-backed RAG answer streaming. No Streamlit deps."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterator

from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

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


@lru_cache(maxsize=4)
def load_llm(model_name: str) -> ChatGroq:
    return ChatGroq(
        model=model_name,
        temperature=0.6,
        max_tokens=4096,
        reasoning_format="hidden",
        reasoning_effort="high",
        model_kwargs={"top_p": 0.95},
    )


def stream_answer(question: str, history: str, docs, model_name: str) -> Iterator[str]:
    """Yields raw text chunks from the model."""
    composed = f"Previous conversation:\n{history}\n\nCurrent question: {question}" if history else question
    chain = create_stuff_documents_chain(load_llm(model_name), ANSWER_PROMPT, document_prompt=DOCUMENT_PROMPT)
    for chunk in chain.stream({"input": composed, "context": docs}):
        if isinstance(chunk, str):
            yield chunk
        elif hasattr(chunk, "content") and isinstance(chunk.content, str) and chunk.content:
            yield chunk.content


def clean_reply(raw: str) -> str:
    return THINK_PATTERN.sub("", raw or "").strip()


def docs_to_sources(docs) -> list[dict]:
    return [
        {
            "source": d.metadata.get("source", "PDF"),
            "page": d.metadata.get("page", "-"),
            "snippet": d.page_content[:240].replace("\n", " "),
            "ocr": bool(d.metadata.get("ocr")),
        }
        for d in docs
    ]

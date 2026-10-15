"""Predefined document intelligence tasks (via RAG chat pipeline)."""

from __future__ import annotations

from atbot.i18n import t

TASK_KEYS = ("ask", "summary", "translate", "key_points", "explain")


def prompt_for_task(task: str) -> str | None:
    mapping = {
        "summary": "prompt_summary",
        "ask": "prompt_ask",
        "key_points": "prompt_key_points",
        "explain": "prompt_explain",
        "translate": "prompt_translate_chat",
    }
    key = mapping.get(task)
    return t(key) if key else None

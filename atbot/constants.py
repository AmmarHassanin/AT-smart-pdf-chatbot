from pathlib import Path

ROBOT_IMAGE = Path(__file__).resolve().parent.parent / "assets" / "Layer 1.png"

MAX_UPLOAD_MB = 200

MODELS = {
    "دقيق — GPT-OSS 120B": "openai/gpt-oss-120b",
    "سريع — GPT-OSS 20B": "openai/gpt-oss-20b",
}

SUGGESTIONS = [
    "Summarize this document",
    "Explain the key concepts",
    "Generate multiple-choice questions",
    "Extract the most important notes",
]

SESSION_DEFAULTS = {
    "chats": {},
    "active_chat_id": None,
    "ui_lang": "en",
    "ui_theme": "dark",
    "chat_search": "",
    "rename_chat_id": None,
    "pending_delete_id": None,
    "show_translate_panel": False,
    "answer_in_progress": False,
}

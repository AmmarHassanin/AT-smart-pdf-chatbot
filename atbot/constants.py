from pathlib import Path

ROBOT_IMAGE = Path(__file__).resolve().parent.parent / "assets" / "at-robot.jpg"

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
}

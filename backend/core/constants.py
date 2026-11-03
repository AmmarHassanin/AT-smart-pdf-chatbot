MAX_UPLOAD_MB = 200

MODELS = {
    "accurate": "openai/gpt-oss-120b",
    "fast": "openai/gpt-oss-20b",
}

SUGGESTIONS = [
    "Summarize this document",
    "Explain the key concepts",
    "Generate multiple-choice questions",
    "Extract the most important notes",
]

TASK_PROMPTS = {
    "summary": "Provide a concise summary and a short detailed summary of this document using only the PDF context.",
    "ask": "What are the most important things I should know from this document?",
    "key_points": "Extract the key points as clear bullet lists grouped by topic. Use only the document.",
    "explain": "Explain the most difficult parts of this document in simple language for a beginner.",
    "translate": "List important passages from the document and give their meaning (stay within document facts only).",
}

"""Extract text from in-memory PDF bytes (for translation / previews)."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

MAX_TRANSLATE_CHARS = 12_000


def extract_text_from_files(files: dict[str, bytes], *, max_chars: int = MAX_TRANSLATE_CHARS) -> str:
    parts: list[str] = []
    total = 0
    for name, data in files.items():
        try:
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted and reader.decrypt("") == 0:
                continue
        except Exception:
            continue
        for number, page in enumerate(reader.pages, start=1):
            try:
                chunk = (page.extract_text() or "").strip()
            except Exception:
                chunk = ""
            if not chunk:
                continue
            block = f"--- {name} · p.{number} ---\n{chunk}\n"
            if total + len(block) > max_chars:
                remaining = max_chars - total
                if remaining > 80:
                    parts.append(block[:remaining] + "\n…")
                break
            parts.append(block)
            total += len(block)
        if total >= max_chars:
            break
    return "\n".join(parts).strip()


def primary_pdf(files: dict[str, bytes]) -> tuple[str, bytes] | None:
    if not files:
        return None
    name = next(iter(files.keys()))
    return name, files[name]

"""OCR fallback for scanned PDF pages (no embedded text layer)."""

from __future__ import annotations

from functools import lru_cache

OCR_ZOOM = 2.0


@lru_cache(maxsize=1)
def _load_engine():
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def ocr_pdf_pages(data: bytes, page_numbers: list[int]) -> dict[int, str]:
    """Run OCR on the given 1-indexed page numbers of a PDF. Returns {page_number: text}."""
    if not page_numbers:
        return {}
    import pymupdf

    engine = _load_engine()
    out: dict[int, str] = {}
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception:
        return out

    matrix = pymupdf.Matrix(OCR_ZOOM, OCR_ZOOM)
    for number in page_numbers:
        idx = number - 1
        if idx < 0 or idx >= doc.page_count:
            continue
        try:
            pix = doc[idx].get_pixmap(matrix=matrix)
            img_bytes = pix.tobytes("png")
            result, _ = engine(img_bytes)
        except Exception:
            continue
        if not result:
            continue
        lines = [line[1] for line in result if len(line) > 1 and line[1]]
        text = "\n".join(lines).strip()
        if text:
            out[number] = text
    doc.close()
    return out

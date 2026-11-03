"""PDF text extraction (native + OCR fallback) and FAISS indexing. No Streamlit deps."""

from __future__ import annotations

import hashlib
from functools import lru_cache
from io import BytesIO

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from .ocr import ocr_pdf_pages


@lru_cache(maxsize=1)
def load_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", encode_kwargs={"normalize_embeddings": True})


def file_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_pdf(name: str, data: bytes) -> tuple[list[Document], int, dict | None]:
    """Returns (docs, page_count, warning). warning is a structured dict the caller/UI can localize."""
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted and reader.decrypt("") == 0:
            return [], 0, {"type": "encrypted_pdf", "name": name}
    except Exception:
        return [], 0, {"type": "corrupt_pdf", "name": name}

    docs: list[Document] = []
    pending: dict[int, Document] = {}
    empty_pages: list[int] = []
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = (page.extract_text() or "").strip()
        except Exception:
            text = ""
        doc = Document(page_content=text, metadata={"source": name, "page": number, "ocr": False})
        pending[number] = doc
        if text:
            docs.append(doc)
        else:
            empty_pages.append(number)

    warning = None
    if empty_pages:
        try:
            ocr_results = ocr_pdf_pages(data, empty_pages)
        except Exception:
            ocr_results = {}
        for number, text in ocr_results.items():
            pending[number].page_content = text
            pending[number].metadata["ocr"] = True
            docs.append(pending[number])
        still_empty = len(empty_pages) - len(ocr_results)
        if ocr_results and still_empty > 0:
            warning = {"type": "ocr_partial", "name": name, "count": still_empty}
        elif ocr_results:
            warning = {"type": "ocr_used", "name": name}

    docs.sort(key=lambda d: d.metadata["page"])
    if not docs:
        return [], len(reader.pages), {"type": "no_text_pdf", "name": name}
    return docs, len(reader.pages), warning


def build_index(files: dict[str, bytes]):
    """files: {filename: bytes}. Returns (faiss_store_or_None, total_pages, warnings)."""
    from langchain_community.vectorstores import FAISS

    docs, pages, warnings = [], 0, []
    for name, data in files.items():
        file_docs, file_pages, warning = read_pdf(name, data)
        docs += file_docs
        pages += file_pages
        if warning:
            warnings.append(warning)

    if not docs:
        return None, pages, warnings

    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
    return FAISS.from_documents(chunks, load_embeddings()), pages, warnings

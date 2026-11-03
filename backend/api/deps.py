"""Shared FastAPI dependencies."""

from __future__ import annotations

import re

from fastapi import Header, HTTPException

_UID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)


def resolve_user_id(x_user_id: str | None = Header(default=None)) -> str:
    if not x_user_id or not _UID_PATTERN.match(x_user_id):
        raise HTTPException(status_code=400, detail="Missing or invalid X-User-Id header (expect a UUID).")
    return x_user_id

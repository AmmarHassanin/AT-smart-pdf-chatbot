from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from .api.chats import router as chats_router  # noqa: E402

app = FastAPI(title="AT PDF API")

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chats_router)


@app.get("/api/health")
def health():
    return {"ok": True, "groq_key_set": bool(os.getenv("GROQ_API_KEY"))}

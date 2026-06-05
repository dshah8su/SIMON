"""
SIMON - HTTP Server (for ChatGPT Custom GPT Actions)
Wraps the same OneNote tools as the MCP server, but exposes them as REST endpoints.

Run:
  python src/http_server.py
  → API available at http://localhost:8000

ChatGPT Custom GPT Action schema (paste into GPT editor):
  openapi: 3.1.0
  info:
    title: SIMON OneNote API
    version: 1.0.0
  servers:
    - url: http://localhost:8000   # or your Vercel/ngrok URL
  paths:
    /save:
      post: ...
    /notebooks:
      get: ...
    /health:
      get: ...
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from onenote_client import OneNoteClient
from formatter import ContentFormatter
from config import DEFAULT_NOTEBOOK, DEFAULT_SECTION, HTTP_HOST, HTTP_PORT

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="SIMON - Save In My OneNote",
    description="REST API that saves content to OneNote. Used by ChatGPT Custom GPT Actions.",
    version="1.0.0",
)

# Allow ChatGPT / browser clients to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-initialise the OneNote client
_client: OneNoteClient | None = None


def _get_client() -> OneNoteClient:
    global _client
    if _client is None:
        _client = OneNoteClient()
    return _client


# ── Request / Response models ─────────────────────────────────────────────────

class SaveRequest(BaseModel):
    content:  str = Field(..., description="Text to save to OneNote (plain text or markdown)")
    title:    str = Field("",  description="Page title. Auto-generated with timestamp if empty.")
    notebook: str = Field(DEFAULT_NOTEBOOK, description="OneNote notebook name")
    section:  str = Field(DEFAULT_SECTION,  description="Section inside the notebook")


class SaveResponse(BaseModel):
    success:           bool
    message:           str
    title:             str = ""
    notebook:          str = ""
    section:           str = ""
    one_note_web_url:  str = ""
    one_note_app_url:  str = ""


class NotebooksResponse(BaseModel):
    notebooks: list[str]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    """Returns 200 OK — used by ChatGPT to verify the server is reachable."""
    return {"status": "ok", "service": "SIMON"}


@app.post("/save", response_model=SaveResponse, tags=["OneNote"])
def save_to_onenote(req: SaveRequest) -> SaveResponse:
    """
    Save content to Microsoft OneNote.

    - Creates the notebook and section automatically if they don't exist.
    - Returns direct links to open the saved page in OneNote web or app.
    """
    try:
        formatter = ContentFormatter()

        title = req.title.strip()
        if not title:
            title = formatter.format_page_title()

        result = _get_client().save_page(
            content=req.content,
            title=title,
            notebook_name=req.notebook,
            section_name=req.section,
        )

        web_url = result.get("oneNoteWebUrl", "")
        app_url = result.get("oneNoteClientUrl", "")

        msg = f"✅ Saved '{title}' to {req.notebook} → {req.section}."
        if web_url:
            msg += f" Open: {web_url}"

        return SaveResponse(
            success=True,
            message=msg,
            title=result.get("title", title),
            notebook=result.get("notebook", req.notebook),
            section=result.get("section", req.section),
            one_note_web_url=web_url,
            one_note_app_url=app_url,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/notebooks", response_model=NotebooksResponse, tags=["OneNote"])
def list_notebooks() -> NotebooksResponse:
    """Return all OneNote notebook names for the authenticated user."""
    try:
        notebooks = _get_client().list_notebooks()
        names = [nb["displayName"] for nb in notebooks]
        return NotebooksResponse(notebooks=names)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n🚀 SIMON HTTP server starting on http://{HTTP_HOST}:{HTTP_PORT}")
    print(f"   Docs: http://localhost:{HTTP_PORT}/docs\n")
    uvicorn.run("http_server:app", host=HTTP_HOST, port=HTTP_PORT, reload=False)

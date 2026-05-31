"""
SIMON - Configuration & Constants
Loads settings from .env and provides defaults for OneNote structure.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

# ── Azure / Microsoft Identity ──────────────────────────────────────────────
AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
# "consumers" = personal Microsoft accounts (outlook.com, live.com, hotmail.com)
# Replace with your tenant ID for work/school (Azure AD) accounts
AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "consumers")

# OAuth scopes required by the OneNote API
GRAPH_SCOPES: list[str] = ["Notes.ReadWrite"]

# ── Token Cache ──────────────────────────────────────────────────────────────
# Stored locally so the user only authenticates once
TOKEN_CACHE_PATH: Path = Path(__file__).parent.parent / "config" / "token_cache.bin"
TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── OneNote Defaults ─────────────────────────────────────────────────────────
DEFAULT_NOTEBOOK: str = os.getenv("ONENOTE_DEFAULT_NOTEBOOK", "AI")
DEFAULT_SECTION: str  = os.getenv("ONENOTE_DEFAULT_SECTION",  "Claude Conversation")

# ── Microsoft Graph ──────────────────────────────────────────────────────────
GRAPH_BASE_URL: str = "https://graph.microsoft.com/v1.0"

# ── HTTP server (for Claude.ai integration via ngrok) ────────────────────────
HTTP_HOST: str = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT: int = int(os.getenv("HTTP_PORT", "8000"))

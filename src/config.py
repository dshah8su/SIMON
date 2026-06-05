"""
SIMON - config.py
-----------------
This file is the single source of truth for all settings.
It reads values from the .env file in the project root.
If a value is missing from .env, a sensible default is used.

You should never hardcode secrets here — put them in .env instead.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load the .env file
# Path(__file__) = this file (src/config.py)
# .parent        = the src/ folder
# .parent.parent = the project root (SIMON/)
# ---------------------------------------------------------------------------
load_dotenv(Path(__file__).parent.parent / ".env")


# ---------------------------------------------------------------------------
# AZURE / MICROSOFT IDENTITY
# These values come from your Azure App Registration at portal.azure.com
# ---------------------------------------------------------------------------

# Your Azure App's unique ID — paste it into .env as AZURE_CLIENT_ID
AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")

# "consumers" means personal Microsoft accounts (outlook.com, live.com, hotmail.com, gmail linked to MS)
# If you have a work/school account, replace with your Azure tenant ID
AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "consumers")

# The permission SIMON needs to read and write to OneNote
# "Notes.ReadWrite" = can create/edit pages in any notebook
GRAPH_SCOPES: list[str] = ["Notes.ReadWrite"]


# ---------------------------------------------------------------------------
# TOKEN CACHE
# After you sign in once, the access token is saved here so SIMON
# does not ask you to sign in again for ~90 days.
# The file is created automatically — you never need to touch it.
# ---------------------------------------------------------------------------
TOKEN_CACHE_PATH: Path = Path(__file__).parent.parent / "config" / "token_cache.bin"
TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)  # create the folder if it doesn't exist


# ---------------------------------------------------------------------------
# ONENOTE DEFAULTS
# These control where SIMON saves notes by default.
# You can override them in .env without changing code.
# ---------------------------------------------------------------------------

# The OneNote notebook to save into (created automatically if it doesn't exist)
DEFAULT_NOTEBOOK: str = os.getenv("ONENOTE_DEFAULT_NOTEBOOK", "My Notebook")

# The section inside that notebook (created automatically if it doesn't exist)
DEFAULT_SECTION: str = os.getenv("ONENOTE_DEFAULT_SECTION", "Claude Conversation")


# ---------------------------------------------------------------------------
# MICROSOFT GRAPH API
# This is the base URL for all Microsoft Graph API calls.
# v1.0 is the stable production version — do not change this.
# ---------------------------------------------------------------------------
GRAPH_BASE_URL: str = "https://graph.microsoft.com/v1.0"


# ---------------------------------------------------------------------------
# HTTP SERVER (for ChatGPT Actions)
# When you run http_server.py, it starts a local web server on this host/port.
# ChatGPT connects to this server to trigger saves.
# ---------------------------------------------------------------------------
HTTP_HOST: str = os.getenv("HTTP_HOST", "0.0.0.0")   # 0.0.0.0 = accept connections from anywhere
HTTP_PORT: int = int(os.getenv("HTTP_PORT", "8000"))  # default port 8000

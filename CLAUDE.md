# SIMON — CLAUDE.md

This file tells Claude Code everything it needs to know to work on this project.

---

## What This Project Is

SIMON (Save In My OneNote) is a local tool that connects Claude Code to Microsoft OneNote via the Model Context Protocol (MCP). When a user types `/simon` in Claude Code, the last response is saved as a formatted page in their OneNote notebook.

---

## Project Structure

```
SIMON/
├── src/
│   ├── config.py          → Loads all settings from .env
│   ├── auth.py            → Microsoft OAuth2 device code flow
│   ├── onenote_client.py  → Microsoft Graph API calls for OneNote
│   ├── formatter.py       → Markdown to OneNote HTML converter
│   ├── mcp_server.py      → MCP server exposing tools to Claude
│   └── http_server.py     → FastAPI server for ChatGPT Actions
├── config/
│   └── token_cache.bin    → MSAL token cache (auto-created, gitignored)
├── .env                   → Secrets — never commit (gitignored)
├── .env.example           → Template for .env
├── requirements.txt       → Python dependencies
├── CLAUDE.md              → This file
└── README.md              → User-facing setup guide
```

---

## Architecture

```
Claude Code
    │
    │  /simon command
    ▼
.claude/commands/simon.md      ← Claude Code slash command definition
    │
    │  calls MCP tool
    ▼
src/mcp_server.py              ← MCP server (runs as subprocess)
    │
    │  save_to_onenote(content, title)
    ▼
src/onenote_client.py          ← Microsoft Graph API client
    │
    ├── src/auth.py            ← Gets/refreshes Microsoft access token
    └── src/formatter.py       ← Converts markdown → OneNote HTML
```

---

## Key Files Explained

### `src/config.py`
Single source of truth for all constants. Reads from `.env` using `python-dotenv`.
Key values: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `DEFAULT_NOTEBOOK`, `DEFAULT_SECTION`, `GRAPH_SCOPES`.

### `src/auth.py`
Handles Microsoft authentication using MSAL device code flow.
- First run: prints a URL + code for browser sign-in
- After that: silently refreshes the token from `config/token_cache.bin`
- Token valid ~90 days
- **Windows note:** Do not use emoji in print statements — Windows cp1252 terminal will throw `UnicodeEncodeError`

### `src/onenote_client.py`
Wraps the Microsoft Graph OneNote REST API.
- `list_notebooks()` — GET /me/onenote/notebooks
- `save_page()` — resolves notebook → section → POSTs HTML page
- Auto-creates notebooks and sections if they don't exist
- **Common error:** `OneDrive quota exceeded (400)` — user must free up OneDrive storage

### `src/formatter.py`
Converts plain text / markdown to the HTML structure OneNote requires.
Supports: headings, bold, italic, inline code, fenced code blocks, bullet lists.

### `src/mcp_server.py`
FastMCP server exposing two tools to Claude:
- `save_to_onenote(content, title, notebook, section)` — main save tool
- `list_notebooks()` — shows available notebooks
Entry point: `python src/mcp_server.py`

### `src/http_server.py`
FastAPI REST server for ChatGPT Custom GPT Actions integration.
Run with: `python src/http_server.py` → serves at `http://localhost:8000`
Expose publicly with ngrok: `ngrok http 8000`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `AZURE_CLIENT_ID` | Yes | Azure App Registration client ID |
| `AZURE_TENANT_ID` | No | Default: `consumers` (personal MS accounts) |
| `ONENOTE_DEFAULT_NOTEBOOK` | No | Default: `My Notebook` |
| `ONENOTE_DEFAULT_SECTION` | No | Default: `Claude Conversation` |
| `HTTP_HOST` | No | Default: `0.0.0.0` |
| `HTTP_PORT` | No | Default: `8000` |

---

## MCP Registration

SIMON is registered as an MCP server in Claude Code with the full Python path:

```bash
claude mcp add simon "C:/Users/shahd/AppData/Local/Programs/Python/Python312/python.exe" "C:/Users/shahd/OneDrive/claude_code/SIMON/src/mcp_server.py" --scope user
```

Verify: `claude mcp list` → should show `simon ✓ Connected`

**Important:** Always use the full absolute path to `python.exe`. Using just `python` will fail because Claude Code's shell may not have Python in PATH.

---

## Slash Command

The `/simon` command is defined at:
```
C:\Users\shahd\.claude\commands\simon.md
```

Two modes:
- `/simon` — saves last response verbatim
- `/simon summarize this` — summarizes, shows preview, asks for confirmation

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# First-time auth (opens browser sign-in)
python -c "import sys; sys.path.insert(0, 'src'); from auth import MicrosoftAuth; MicrosoftAuth().get_token()"

# Start MCP server (Claude Code does this automatically)
python src/mcp_server.py

# Start HTTP server (for ChatGPT)
python src/http_server.py
```

---

## Testing

```bash
# Test 1 — list notebooks
python -c "import sys; sys.path.insert(0,'src'); from onenote_client import OneNoteClient; [print('-',n['displayName']) for n in OneNoteClient().list_notebooks()]"

# Test 2 — save a page
python -c "import sys; sys.path.insert(0,'src'); from onenote_client import OneNoteClient; r = OneNoteClient().save_page('Test content','Test Page','My Notebook','Claude Conversation'); print(r['oneNoteWebUrl'])"
```

---

## Known Issues & Fixes

| Issue | Fix |
|---|---|
| `AADSTS70002: client must be marked as mobile` | Azure portal → App → Authentication → Allow public client flows → Yes |
| `ValueError: offline_access is reserved` | Remove `offline_access` from `GRAPH_SCOPES` — MSAL adds it automatically |
| `OneDrive quota exceeded (400)` | User must free storage at onedrive.live.com |
| `UnicodeEncodeError on emoji` | Replace emoji with plain text e.g. `[OK]` instead of `✅` |
| `MCP server failed to connect` | Use full absolute path to python.exe in MCP registration |
| `mmap failed: Invalid argument` | Git inside OneDrive folder — commit from a local non-OneDrive path instead |
| `Device code expired` | Code valid for 15 min only — re-run auth to get a new code |

---

## Dependencies

| Package | Purpose |
|---|---|
| `mcp[cli]` | Model Context Protocol server framework |
| `msal` | Microsoft Authentication Library (OAuth2) |
| `requests` | HTTP calls to Microsoft Graph API |
| `fastapi` + `uvicorn` | HTTP server for ChatGPT Actions |
| `pydantic` | Request/response validation for HTTP server |
| `python-dotenv` | Loads `.env` file into environment variables |

---

## Security Notes

- `.env` and `config/token_cache.bin` are gitignored — never commit them
- Only `Notes.ReadWrite` permission is requested — no access to email, calendar, or files
- Token is stored locally only — never sent to any third-party server
- The Azure App is registered as a public client (no client secret needed)

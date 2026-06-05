# SIMON — Claude Code Project Context

SIMON (Save In My OneNote) is a personal MCP server that saves Claude conversations to Microsoft OneNote via the Microsoft Graph API.

## Architecture

```
User types SIMON / /simon
        ↓
Claude calls list_sections → user picks section
        ↓
Claude calls save_to_onenote(content, title, section)
        ↓
onenote_client.py → Microsoft Graph API → OneNote page created
```

Two server modes:
- **Claude Code** — `src/mcp_server.py` runs locally via stdio, registered with `claude mcp add`
- **Claude.ai** — `src/http_mcp_server.py` runs over HTTP/SSE with OAuth, tunnelled via ngrok

## Key Files

| File | Purpose |
|------|---------|
| `src/mcp_server.py` | MCP server for Claude Code (stdio transport) |
| `src/http_mcp_server.py` | MCP server for Claude.ai (SSE + OAuth) |
| `src/onenote_client.py` | Microsoft Graph API client — lists notebooks/sections, saves pages |
| `src/auth.py` | Microsoft MSAL auth — device code flow, token cache |
| `src/formatter.py` | Converts markdown to OneNote HTML |
| `src/config.py` | All settings loaded from `.env` |
| `src/session_popup.py` | tkinter popup shown at startup — displays ngrok URL + steps |
| `start_simon_ngrok.ps1` | PowerShell startup script — launches ngrok + server + popup |
| `.claude/commands/simon.md` | Claude Code skill definition for `/simon` command |

## MCP Tools Exposed

| Tool | Description |
|------|-------------|
| `list_sections(notebook)` | Lists all sections in the AI notebook — always call before saving |
| `save_to_onenote(content, title, notebook, section)` | Saves content as a new OneNote page |
| `list_notebooks()` | Lists all notebooks in the Microsoft account |

## /simon Command Workflow

1. Call `list_sections` → show user their existing sections
2. User picks a section or names a new one
3. Derive a short descriptive title from the conversation topic (never use timestamps)
4. Call `save_to_onenote` with chosen section + title
5. Confirm with the returned OneNote URL

## Environment Variables (.env)

```env
AZURE_CLIENT_ID=        # Azure App Registration client ID
AZURE_TENANT_ID=consumers
ONENOTE_DEFAULT_NOTEBOOK=AI
ONENOTE_DEFAULT_SECTION=Claude Conversation
HTTP_HOST=0.0.0.0
HTTP_PORT=8000
```

## ngrok Setup

- Static domain: `curtly-resonate-smilingly.ngrok-free.dev`
- ngrok path: `C:\Users\shahd\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe`
- Auth token: already configured in ngrok config
- Desktop shortcut: "Start SIMON" on Desktop launches `start_simon_ngrok.ps1`
- Claude.ai connector URL: `https://curtly-resonate-smilingly.ngrok-free.dev/sse` (permanent, never changes)

## Known Fixes Applied

**MCP SDK grant_types validation** — Claude.ai only sends `authorization_code` but the SDK requires `refresh_token` too. Fixed by patching:
`C:\Users\shahd\AppData\Local\Programs\Python\Python312\Lib\site-packages\mcp\server\auth\handlers\register.py` (line 76 — removed the strict grant_types check)

**FastMCP.run() signature** — `host` and `port` go in the constructor (`FastMCP(..., host=..., port=...)`), not in `mcp.run(transport="sse")`.

**Git + OneDrive** — Never commit from the OneDrive path (`C:\Users\shahd\OneDrive\claude_code\SIMON`). Always use the local clone at `C:\Projects\SIMON`. OneDrive breaks git's mmap and file locking.

## Running Locally

**Claude Code (no extra steps):**
```
# Already registered via claude mcp add
# Just type SIMON in any Claude Code session
```

**Claude.ai:**
```powershell
# Double-click "Start SIMON" shortcut on Desktop
# OR run manually:
powershell -ExecutionPolicy Bypass -File "C:\Projects\SIMON\start_simon_ngrok.ps1"
```

## Dependencies

```
msal>=1.37.0          # Microsoft auth
requests>=2.34.2      # Graph API HTTP calls
python-dotenv>=1.2.2  # .env loading
mcp>=1.27.2           # MCP SDK (includes FastMCP, uvicorn, starlette)
pydantic>=2.13.4      # Data validation
uvicorn>=0.48.0       # ASGI server
starlette>=1.2.0      # HTTP framework
# tkinter — built into Python, no install needed
```

## Documentation Files

| File | Audience |
|------|----------|
| `README.md` | Everyone — full setup guide |
| `HOW_IT_ALL_WORKS.md` | Non-technical — big picture diagram |
| `MCP_EXPLAINED.md` | Non-technical — what MCP is |
| `MICROSOFT_GRAPH.md` | Non-technical — what Microsoft Graph is |
| `NGROK.md` | Non-technical — what ngrok does, free vs paid |
| `CLAUDE_AI_SETUP.md` | Step-by-step Claude.ai + ngrok setup |
| `SESSION_POPUP.md` | Popup explained |

## Planned Enhancements

- Cloudflare Tunnel as free alternative to ngrok (eliminates URL changes without paying)

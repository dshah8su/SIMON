# SIMON — Save In My OneNote

> Save your Claude AI conversations directly to Microsoft OneNote with a single word.

**Works with:** Claude Code (CLI/desktop) · Claude.ai (web & mobile)
**Cost:** Free — uses your own Microsoft account and Microsoft Graph API

---

## What Does SIMON Do?

You are in the middle of a conversation with Claude. Claude gives you something useful — an explanation, a plan, a piece of code. You want to keep it.

Instead of copying and pasting, you just type **SIMON**.

Claude saves the conversation to your Microsoft OneNote automatically, and gives you a direct link to the saved page.

---

## Quick Start

| I use... | Go to... |
|----------|----------|
| Claude Code (terminal or desktop app) | [Claude Code Setup](#claude-code-setup) |
| Claude.ai in my browser or phone | [Claude.ai Setup](#claudeai-setup) |
| Both | Do Claude Code Setup first, then Claude.ai Setup |

---

## How to Use It

Once set up, just type in Claude:

```
SIMON
```

or

```
/simon
```

or say naturally:

```
Save this to OneNote
```

Claude saves the last response and returns a direct link to the saved page in OneNote.

---

## Claude Code Setup

### Requirements
- Python 3.12+
- Claude Code installed ([get it here](https://claude.ai/code))
- A Microsoft account (Outlook, Hotmail, or any account linked to Microsoft)
- OneNote activated — sign in at [onenote.com](https://onenote.com) at least once
- An Azure App Registration (free, takes 5 minutes — instructions below)

### Step 1 — Clone and install

```bash
git clone https://github.com/dshah8su/SIMON.git
cd SIMON
pip install -r requirements.txt
```

### Step 2 — Create an Azure App Registration

This is the one-time setup that gives SIMON permission to access your OneNote.

1. Go to **[portal.azure.com](https://portal.azure.com)** and sign in with your Microsoft account
2. Search for **"App registrations"** at the top → click **+ New registration**
3. Fill in:
   - **Name:** `SIMON`
   - **Supported account types:** Personal Microsoft accounts only
   - **Redirect URI:** Public client/native → `http://localhost`
4. Click **Register** → copy the **Application (client) ID** shown on the next page
5. Go to **Authentication** → scroll down → enable **"Allow public client flows"** → Save
6. Go to **API permissions** → Add a permission → Microsoft Graph → Delegated → search `Notes.ReadWrite` → Add

> **Why Azure?** SIMON needs Microsoft's permission to write to OneNote on your behalf. The Azure App Registration is the official way to get that. It's free and takes 5 minutes.

### Step 3 — Configure your settings

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
AZURE_CLIENT_ID=paste-your-client-id-here
AZURE_TENANT_ID=consumers
ONENOTE_DEFAULT_NOTEBOOK=AI
ONENOTE_DEFAULT_SECTION=Claude Conversation
```

### Step 4 — Register SIMON with Claude Code

```bash
claude mcp add simon "C:/full/path/to/python.exe" "C:/full/path/to/SIMON/src/mcp_server.py" --scope user
claude mcp list
```

You should see `simon ✓ Connected`.

> To find your Python path: run `where python` on Windows or `which python3` on Mac/Linux

### Step 5 — First sign-in

The first time you use SIMON, it will show:

```
1. Open this URL: https://microsoft.com/devicelogin
2. Enter this code: SHRKVAJ4
3. Sign in with your Microsoft account
```

Open the URL, enter the code, sign in. SIMON saves the token — you won't be asked again for ~90 days.

### Step 6 — Test it

In Claude Code, type `/simon`. Claude saves the last response to OneNote and returns a link.

---

## Claude.ai Setup

Claude.ai (the web and mobile app) needs an extra step because it runs in the cloud and cannot reach SIMON directly on your PC. We use **ngrok** to create a secure tunnel.

For the full step-by-step guide, see: **[CLAUDE_AI_SETUP.md](CLAUDE_AI_SETUP.md)**

Short version:
1. Install ngrok: `winget install ngrok.ngrok`
2. Get a free auth token at [dashboard.ngrok.com](https://dashboard.ngrok.com)
3. Run `start_simon_ngrok.ps1` — a popup shows the URL and steps
4. Add SIMON as a connector in Claude.ai settings with the URL shown
5. Click Approve on the browser page that opens

---

## Project Structure

```
SIMON/
├── src/
│   ├── mcp_server.py         → MCP server for Claude Code (local connection)
│   ├── http_mcp_server.py    → MCP server for Claude.ai (internet, with OAuth)
│   ├── session_popup.py      → Startup popup showing ngrok URL + setup steps
│   ├── onenote_client.py     → Microsoft Graph API wrapper for OneNote
│   ├── auth.py               → Microsoft sign-in and token management
│   ├── formatter.py          → Converts markdown to OneNote HTML
│   └── config.py             → All settings, loaded from .env
├── config/
│   └── token_cache.bin       → Your login token (auto-created, never committed)
├── start_simon_ngrok.ps1     → Startup script for Claude.ai (starts everything)
├── .env                      → Your secrets (never committed)
├── .env.example              → Template — copy this to .env
└── requirements.txt          → Python packages SIMON needs
```

---

## Documentation

| File | What it explains |
|------|-----------------|
| [HOW_IT_ALL_WORKS.md](HOW_IT_ALL_WORKS.md) | Big picture — how every piece connects |
| [CLAUDE_AI_SETUP.md](CLAUDE_AI_SETUP.md) | Step-by-step Claude.ai + ngrok setup |
| [MCP_EXPLAINED.md](MCP_EXPLAINED.md) | What MCP is and how Claude uses it |
| [MICROSOFT_GRAPH.md](MICROSOFT_GRAPH.md) | What Microsoft Graph is and why SIMON needs it |
| [NGROK.md](NGROK.md) | What ngrok does, free vs paid, alternatives |
| [SESSION_POPUP.md](SESSION_POPUP.md) | The startup popup — why it exists, how to remove it |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `AZURE_CLIENT_ID is not set` | Copy `.env.example` → `.env` and fill in your Client ID |
| `AADSTS70002: client must be marked as mobile` | Azure portal → App → Authentication → Allow public client flows → Yes |
| `MCP server failed to connect` | Use the full absolute path to `python.exe` when registering |
| Saved page not visible in OneNote desktop | Press `Shift+F9` in OneNote to force sync |
| ngrok "version too old" error | Run `ngrok update` in your terminal |
| Claude.ai "Couldn't register" error | Wait a few seconds then try adding the connector again |

---

## Security

- Your Microsoft token is stored in `config/token_cache.bin` — on your PC only, never uploaded
- `.env` with your Client ID is gitignored — never shared
- SIMON only requests `Notes.ReadWrite` — no access to email, files, or calendar
- Your conversation content is never stored anywhere except your own OneNote

---

## License

MIT — free to use, modify, and share.

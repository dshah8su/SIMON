# SIMON — Save In My OneNote

> Save your AI conversations from Claude directly to Microsoft OneNote with a single command.

**Works with:** Claude Code (via MCP) · ChatGPT (via Custom GPT Actions)  
**Cost:** Free — uses Microsoft Graph API with your personal Microsoft account

---

## What It Does

| Command | Result |
|---|---|
| `/simon` | Saves the last Claude response to OneNote instantly |
| `/simon summarize this` | Summarizes first, shows preview, asks to confirm, then saves |

---

## How It Works

```
You type /simon in Claude Code
         ↓
Claude calls the SIMON MCP server (running locally on your machine)
         ↓
SIMON authenticates with Microsoft (one-time sign-in, token cached ~90 days)
         ↓
Microsoft Graph API creates a formatted page in your OneNote
         ↓
Claude replies with a direct link to the saved page
```

---

## Project Structure

```
SIMON/
├── src/
│   ├── config.py          → All settings, loaded from .env
│   ├── auth.py            → Microsoft OAuth sign-in (device code flow)
│   ├── onenote_client.py  → Microsoft Graph API wrapper for OneNote
│   ├── formatter.py       → Converts markdown to OneNote HTML
│   ├── mcp_server.py      → MCP server Claude Code connects to
│   └── http_server.py     → REST API for ChatGPT Actions
├── config/
│   └── token_cache.bin    → Saved login token (auto-created, never commit)
├── .env                   → Your secrets (never commit this)
├── .env.example           → Template for .env
└── requirements.txt       → Python dependencies
```

---

## Requirements

- Python 3.12+
- A Microsoft account (outlook.com, hotmail.com, or Gmail linked to Microsoft)
- OneNote activated — sign in at onenote.com at least once
- OneDrive with free space (Microsoft blocks writes when storage is full)
- Claude Code installed
- An Azure App Registration (free, 5 minutes — instructions below)

---

## Setup

### Step 1 — Install dependencies

```bash
git clone https://github.com/dshah8su/SIMON.git
cd SIMON
pip install -r requirements.txt
```

### Step 2 — Create an Azure App Registration

1. Go to **portal.azure.com** and sign in
2. Search **"App registrations"** → click **+ New registration**
3. Fill in:
   - Name: `SIMON`
   - Supported account types: **Personal Microsoft accounts only**
   - Redirect URI: `Public client/native` → `http://localhost`
4. Click **Register** → copy the **Application (client) ID**
5. Go to **Authentication** → enable **"Allow public client flows"** → Save
   *(Without this, sign-in will fail with error AADSTS70002)*
6. Go to **API permissions** → Add a permission → Microsoft Graph → Delegated → add `Notes.ReadWrite`

### Step 3 — Configure .env

```bash
cp .env.example .env
```

Edit `.env`:

```env
AZURE_CLIENT_ID=paste-your-client-id-here
AZURE_TENANT_ID=consumers
ONENOTE_DEFAULT_NOTEBOOK=My Notebook
ONENOTE_DEFAULT_SECTION=Claude Conversation
```

### Step 4 — Register with Claude Code

```bash
claude mcp add simon "C:/full/path/to/python.exe" "C:/full/path/to/SIMON/src/mcp_server.py" --scope user
claude mcp list   # should show: simon ✓ Connected
```

> Find your Python path: run `where python` on Windows or `which python3` on Mac/Linux

### Step 5 — First sign-in

On first use, SIMON will print a URL and a code. Open the URL in your browser, enter the code, and sign in with your Microsoft account. Token is saved — you won't be asked again for ~90 days.

### Step 6 — Test it

In Claude Code, type `/simon` — Claude saves the last response to OneNote and returns a link.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `AZURE_CLIENT_ID is not set` | `.env` not configured | Copy `.env.example` → `.env` and fill in your Client ID |
| `AADSTS70002: client must be marked as mobile` | Public client flows off | Azure portal → App → Authentication → Allow public client flows → Yes |
| `offline_access is reserved` | Wrong scope in config | Only use `Notes.ReadWrite` — MSAL adds offline_access automatically |
| `OneDrive quota exceeded` | Storage full | Free up space at onedrive.live.com and empty the Recycle Bin |
| `UnicodeEncodeError on emoji` | Windows terminal issue | Use plain text like `[OK]` instead of emoji in print statements |
| `MCP server failed to connect` | Wrong Python path | Use the full absolute path to python.exe when registering |
| `Device code expired` | Took over 15 minutes | Re-run — a new code is generated each time |

---

## Security

- Token stored locally in `config/token_cache.bin` — gitignored, never leaves your machine
- `.env` with Client ID is gitignored
- Only `Notes.ReadWrite` permission requested — nothing else
- No conversation data stored anywhere except your own OneNote

---

## License

MIT — free to use, modify, and share.

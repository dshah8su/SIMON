# SIMON — Setup Guide

Complete setup instructions for new users. Follow this top to bottom — the order matters.

---

## Base Requirements

| Requirement | Why |
|---|---|
| Python 3.12+ | Must be on PATH (`python --version` to check) |
| Microsoft account | outlook.com, hotmail.com, or Gmail linked to Microsoft |
| OneNote activated | Sign in at onenote.com at least once — Microsoft blocks API writes otherwise |
| OneDrive with free space | SIMON writes pages to OneDrive-backed OneNote |
| Azure App Registration | Provides the credentials SIMON uses to talk to Microsoft Graph API |
| Claude Code **or** Claude.ai account | Where you'll use the `/simon` command |
| ngrok (Claude.ai only) | Exposes the local server publicly so Claude.ai can reach it |

---

## Step 1 — Clone and install

```bash
git clone https://github.com/dshah8su/SIMON.git
cd SIMON
pip install -r requirements.txt
```

---

## Step 2 — Create an Azure App Registration

This is a one-time step that gives SIMON permission to write to your OneNote.

1. Go to [portal.azure.com](https://portal.azure.com) and sign in with your Microsoft account
2. Search **"App registrations"** → click **+ New registration**
3. Fill in:
   - Name: `SIMON` (or anything you like)
   - Supported account types: **Personal Microsoft accounts only**
   - Redirect URI: `http://localhost:8400`
4. Click **Register**
5. Copy the **Application (client) ID** — you'll need it in Step 3

**Add API permissions:**
1. In your app → **API permissions** → **+ Add a permission**
2. Choose **Microsoft Graph** → **Delegated permissions**
3. Add these four: `Notes.Create`, `Notes.Read`, `Notes.ReadWrite`, `offline_access`
4. Click **Grant admin consent**

---

## Step 3 — Create your `.env` file

Copy the template and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
AZURE_CLIENT_ID=your-application-client-id-from-step-2
AZURE_TENANT_ID=consumers
DEFAULT_NOTEBOOK=AI
DEFAULT_SECTION=Claude Conversation
```

`DEFAULT_NOTEBOOK` and `DEFAULT_SECTION` are where SIMON saves by default. Change them to match your OneNote structure.

---

## Step 4 — First sign-in (Microsoft OAuth)

Run this once to authenticate with Microsoft:

```bash
python src/auth.py
```

It will print a URL and a code. Open the URL in your browser, enter the code, and sign in with your Microsoft account. The token is saved to `config/token_cache.bin` and stays valid for ~90 days.

---

## Step 5 — Connect to Claude

### Option A — Claude Code (CLI)

Register SIMON as a local MCP server:

```bash
claude mcp add simon python /absolute/path/to/SIMON/src/mcp_server.py
```

Then in any Claude Code session, type `/simon` to save the last response to OneNote.

### Option B — Claude.ai (web) or Claude desktop

SIMON needs to be reachable over HTTPS. ngrok provides this.

**Install ngrok:**
1. Download from [ngrok.com/download](https://ngrok.com/download)
2. Create a free account at [dashboard.ngrok.com](https://dashboard.ngrok.com)
3. Run `ngrok authtoken <your-token>` once (token is in your ngrok dashboard)

**Start SIMON for Claude.ai:**

```powershell
powershell -ExecutionPolicy Bypass -File start_simon_ngrok.ps1
```

The script will print a URL like:
```
Add this URL to Claude.ai MCP settings:
  https://xxxx.ngrok-free.app/sse
```

**Add to Claude.ai:**
1. Go to Claude.ai → **Settings** → **Integrations**
2. Click **Add integration**
3. Paste the `/sse` URL from above
4. An approval page will open in your browser — click **Approve**
5. SIMON tools are now available in your Claude.ai session

---

## Common Issues

### "Token not found" or sign-in prompt on every run
The `config/token_cache.bin` file is missing or expired. Run `python src/auth.py` again.

### "OneDrive quota exceeded (400)"
Your OneDrive storage is full. Free up space at [onedrive.live.com](https://onedrive.live.com).

### "Tool not found" on Claude.ai
The ngrok URL changed (free tier gives a new URL every restart). Re-run `start_simon_ngrok.ps1` and update the URL in Claude.ai → Settings → Integrations.

### ngrok fails to start
Make sure you ran `ngrok authtoken <token>` at least once. Without authentication, ngrok exits silently.

### OneNote notebook not found
Sign in at [onenote.com](https://onenote.com) first. Microsoft does not create the OneNote backend until you open OneNote at least once.

### Unicode/emoji error on Windows terminal
Set `PYTHONIOENCODING=utf-8` in your environment, or add it to your `.env` file.

---

## How it works (quick summary)

```
You type /simon
      ↓
Claude calls the SIMON MCP server
      ↓
SIMON authenticates with Microsoft (token cached ~90 days)
      ↓
Microsoft Graph API creates a formatted page in OneNote
      ↓
Claude replies with a direct link to the saved page
```

For Claude Code, the server runs as a local subprocess over stdio.
For Claude.ai, the server runs over HTTP/SSE behind an ngrok tunnel.

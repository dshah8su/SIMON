# Claude.ai Setup Guide

This guide walks you through connecting SIMON to the Claude.ai web and mobile app.
If you only use Claude Code (the developer CLI), you don't need this — see `README.md` instead.

---

## Before You Start

Make sure you have already completed the base SIMON setup:
- ✅ Python 3.12+ installed
- ✅ SIMON cloned and dependencies installed (`pip install -r requirements.txt`)
- ✅ Azure App Registration created and `.env` configured
- ✅ Microsoft sign-in completed at least once (`python src/mcp_server.py` to trigger it)

If any of these are missing, complete `README.md` first, then come back here.

---

## What You're Building

```
Claude.ai  →  internet  →  ngrok  →  your PC  →  SIMON  →  OneNote
```

ngrok creates a temporary public address for your PC so Claude.ai can reach SIMON.

---

## Step 1 — Install ngrok

Open a terminal and run:

```
winget install ngrok.ngrok
```

Close and reopen your terminal after this (so the new command is recognised).

---

## Step 2 — Create a Free ngrok Account

1. Go to **dashboard.ngrok.com** and sign up (free, no credit card required for basic use)
2. After signing in, go to **Your Authtoken** in the left sidebar
3. Copy the token shown there

---

## Step 3 — Save Your ngrok Auth Token

In your terminal, run:

```
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with the token you copied. You only do this once.

---

## Step 4 — Start SIMON for Claude.ai

Every time you want to use SIMON in Claude.ai, run this script:

```
powershell -ExecutionPolicy Bypass -File "C:\path\to\SIMON\start_simon_ngrok.ps1"
```

The script will:
1. Start ngrok and get a public URL
2. Start the SIMON HTTP server with that URL
3. Open a popup window showing the URL and next steps

---

## Step 5 — Add SIMON as a Connector in Claude.ai

After the popup appears:

1. Open **Claude.ai** in your browser or desktop app
2. Go to **Settings → Integrations** (also called Connectors)
3. Click **Add** (or **+ New Connector**)
4. Fill in:
   - **Name:** `SIMON`
   - **URL:** paste the URL from the popup — it ends with `/sse`
5. Click **Save**

---

## Step 6 — Approve the OAuth Connection

After saving the connector, Claude.ai will open a browser tab to an approval page.

This page is served by SIMON running on your own PC. It looks like:

```
┌─────────────────────────────────────┐
│  SIMON — Save to OneNote            │
│                                     │
│  Claude.ai is requesting permission │
│  to save your conversations to      │
│  Microsoft OneNote.                 │
│                                     │
│  [  Approve  ]                      │
└─────────────────────────────────────┘
```

Click **Approve**. SIMON is now connected to Claude.ai.

---

## Step 7 — Test It

In any Claude.ai chat, type:

> "Save this conversation to OneNote"

Claude will use SIMON to save the response and return a link to the saved page.

---

## Every Session After That (Free ngrok Plan)

Because the free ngrok URL changes each time you restart, you need to update the connector each session:

1. Run `start_simon_ngrok.ps1`
2. The popup shows the new URL — click **Copy**
3. In Claude.ai: delete the old SIMON connector → add a new one with the new URL
4. Click **Approve** on the browser page that opens

**This takes about 30 seconds once you've done it a couple of times.**

### To skip this entirely — get a fixed URL

- Check **dashboard.ngrok.com → Cloud Edge → Domains** for a free static domain
- Or upgrade to a paid ngrok plan
- Or use Cloudflare Tunnel (see `NGROK.md`)

Once you have a fixed URL, update this one line in `start_simon_ngrok.ps1`:

```powershell
# Change this:
Start-Process $ngrok -ArgumentList "http $PORT" -WindowStyle Hidden

# To this (using your fixed domain):
Start-Process $ngrok -ArgumentList "http --domain=your-domain.ngrok-free.app $PORT" -WindowStyle Hidden
```

Then set up the Claude.ai connector once — it will never need updating again.

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| Popup says "Could not reach ngrok" | ngrok not running | Re-run `start_simon_ngrok.ps1` |
| Claude.ai shows "Couldn't register" | Server not running | Wait 5 seconds and try adding the connector again |
| OAuth approval page doesn't open | Firewall blocked Python | Allow Python through Windows Firewall when prompted |
| Saved page not visible in OneNote desktop | OneDrive sync delay | Press Shift+F9 in OneNote to force sync |
| ngrok auth error — version too old | Old ngrok version | Run `ngrok update` in your terminal |

# SIMON Session Popup

When you start SIMON for Claude.ai, a small popup window appears automatically.
It shows the current connector URL and the steps to update Claude.ai — so you never have to remember anything.

## What the popup does

- Fetches the active ngrok URL from the local ngrok API
- Displays the full connector URL (with `/sse`) ready to copy
- Shows step-by-step instructions for updating the Claude.ai connector
- Stays open while SIMON is running; closing it stops both servers

## Why the popup exists — ngrok free plan

SIMON tunnels your local server to the internet using **ngrok** so Claude.ai (web/mobile) can reach it.

On the **free ngrok plan**, the public URL is randomly generated every session:

```
https://abc123-random.ngrok-free.app   ← changes every restart
```

This means every time you start SIMON you get a new URL, and Claude.ai's connector
needs to be updated with it. The popup automates finding that URL so you only need to:

1. Copy the URL from the popup
2. Delete the old SIMON connector in Claude.ai
3. Add a new one with the new URL

## Upgrading to a paid ngrok plan — popup disappears

If you upgrade to any **paid ngrok plan**, you get a fixed static domain:

```
https://your-name.ngrok-free.app   ← never changes
```

With a static domain:
- The startup script is updated once with your fixed URL
- Claude.ai connector is configured once and never touched again
- **The session popup is no longer needed and will not appear**

To claim a free static domain (ngrok gives one per account on free tier too):
1. Go to **dashboard.ngrok.com → Cloud Edge → Domains**
2. Click **+ New Domain**
3. Share the domain with Claude Code — it will update the startup script automatically

## Files

| File | Purpose |
|------|---------|
| `src/session_popup.py` | The popup window (tkinter) |
| `start_simon_ngrok.ps1` | Startup script — launches ngrok, server, then popup |
| `src/http_mcp_server.py` | SIMON HTTP MCP server with OAuth |

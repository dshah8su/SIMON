# How It All Works — The Big Picture

This page explains how every piece of SIMON connects together.
No technical background needed.

---

## The Journey of a Single Save

When you type "SIMON" in Claude, here is everything that happens:

```
┌─────────────────────────────────────────────────────────────────┐
│  YOU                                                            │
│  Type "SIMON" or "/simon" in Claude                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE                                                         │
│  Recognises the intent to save → calls the SIMON MCP tool      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
┌─────────────────┐      ┌──────────────────────────────────────┐
│  Claude Code    │      │  Claude.ai (web/mobile)              │
│  (local)        │      │  Sends request over the internet     │
│                 │      └────────────────┬─────────────────────┘
│  Talks directly │                       │
│  to local MCP   │                       ▼
│  server         │      ┌──────────────────────────────────────┐
└────────┬────────┘      │  ngrok tunnel                        │
         │               │  Public URL → forwards to your PC    │
         │               └────────────────┬─────────────────────┘
         │                                │
         └───────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  SIMON MCP SERVER  (running on your PC)                        │
│  Receives the save request from Claude                          │
│  Contains: the content to save + a title                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  MICROSOFT AUTH  (auth.py)                                      │
│  Checks if SIMON has a valid token to access OneNote            │
│  If yes → continues. If no → asks you to sign in (first time)  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  MICROSOFT GRAPH API  (onenote_client.py)                      │
│  Finds your "AI" notebook and "Claude Conversation" section     │
│  Creates them if they don't exist yet                           │
│  Saves the content as a formatted HTML page                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  MICROSOFT ONENOTE                                              │
│  Your conversation is now saved as a page                       │
│  Accessible on PC, browser, and mobile OneNote app              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE                                                         │
│  Receives confirmation + OneNote link                           │
│  Shows you: "✅ Saved! Open in OneNote: https://..."           │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Files and What They Do

```
SIMON/
│
├── start_simon_ngrok.ps1     ← Run this to start everything (Claude.ai only)
│                               Starts ngrok + the HTTP server + shows the popup
│
├── src/
│   ├── mcp_server.py         ← The MCP server for Claude Code (local)
│   │                            Claude Code connects here directly
│   │
│   ├── http_mcp_server.py    ← The MCP server for Claude.ai (over internet)
│   │                            Has built-in OAuth so Claude.ai can authenticate
│   │
│   ├── session_popup.py      ← The popup window shown at startup
│   │                            Shows the ngrok URL + steps to update Claude.ai
│   │
│   ├── onenote_client.py     ← Talks to Microsoft Graph to save pages
│   │
│   ├── auth.py               ← Handles Microsoft sign-in and token management
│   │
│   ├── formatter.py          ← Converts your conversation to OneNote HTML format
│   │
│   └── config.py             ← All settings (loaded from .env file)
│
├── config/
│   └── token_cache.bin       ← Your Microsoft login token (auto-created, never shared)
│
├── .env                      ← Your Azure Client ID (secret, never shared)
├── .env.example              ← Template — copy this to .env and fill it in
└── requirements.txt          ← Python packages SIMON needs
```

---

## The Two Ways to Use SIMON

### Option 1 — Claude Code (Simpler)

Best for developers using the Claude Code CLI or desktop app.

```
Prerequisites: Python · Azure App Registration · Claude Code installed
Setup time:    ~10 minutes (one time)
After setup:   Just type "SIMON" in Claude Code — nothing else to run
```

### Option 2 — Claude.ai Web and Mobile (More Steps, More Reach)

Best if you use Claude.ai in your browser or on your phone.

```
Prerequisites: Everything above + ngrok installed + ngrok auth token
Setup time:    ~20 minutes (one time) + ~30 seconds per session
After setup:   Run start_simon_ngrok.ps1 → copy URL → update connector
               (Goes away permanently with a fixed ngrok domain)
```

---

## Glossary

| Term | Plain English meaning |
|------|-----------------------|
| MCP | A standard way for Claude to use external tools |
| MCP server | A small program that listens for Claude's requests and acts on them |
| Microsoft Graph | Microsoft's official API for accessing OneNote, email, files, etc. |
| OAuth | A secure sign-in system that lets apps access your data without knowing your password |
| ngrok | A tool that gives your local PC a public internet address |
| Token | A temporary digital key that proves SIMON has permission to access OneNote |
| SSE | Server-Sent Events — the connection type Claude.ai uses to talk to MCP servers |
| Connector | What Claude.ai calls an MCP server integration in its settings |

---

## Where to Learn More

| Topic | File |
|-------|------|
| Microsoft Graph explained | `MICROSOFT_GRAPH.md` |
| MCP explained | `MCP_EXPLAINED.md` |
| ngrok explained | `NGROK.md` |
| Claude.ai setup steps | `CLAUDE_AI_SETUP.md` |
| Session popup explained | `SESSION_POPUP.md` |
| Full project setup | `README.md` |

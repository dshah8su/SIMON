# MCP (Model Context Protocol) — Plain English Guide

## What is MCP?

Claude is a very capable AI, but out of the box it can only do one thing — **talk**.

It can answer questions, write code, explain things — but it cannot save a file, send an email, or write to your OneNote. It has no hands.

**MCP (Model Context Protocol) gives Claude hands.**

It is a standard way for Claude to connect to external tools — tools that *can* do things in the real world. SIMON is one of those tools.

---

## The Analogy

Think of Claude as a brilliant consultant sitting in a room with no phone, no computer, no internet.

You walk in, describe your problem, and they give you brilliant advice. But they can't actually *do* anything outside that room.

**MCP is like giving that consultant a phone** — a standardised phone that any tool in the world can call or be called from. Now Claude can say "let me call my OneNote tool and save this for you."

---

## How Claude Connects to SIMON

```
You type "/simon" or "SIMON" in Claude
        ↓
Claude recognises it needs the SIMON tool
        ↓
Claude sends a request to the SIMON MCP server (running on your PC)
        ↓
SIMON saves the content to OneNote via Microsoft Graph
        ↓
SIMON sends back a confirmation + OneNote link
        ↓
Claude shows you the result
```

All of this happens in seconds, invisibly.

---

## What is an MCP Server?

An MCP server is just a small program running on your computer that:

1. **Listens** for requests from Claude
2. **Does something** when a request arrives (in SIMON's case: saves to OneNote)
3. **Reports back** the result

SIMON has two MCP servers:

| Server | File | Used for |
|--------|------|----------|
| Local MCP server | `src/mcp_server.py` | Claude Code (CLI/desktop app) |
| HTTP MCP server | `src/http_mcp_server.py` | Claude.ai web and mobile app |

---

## Two Ways Claude Connects

### Claude Code (the developer tool)
Claude Code runs on your PC and can talk directly to a local MCP server. No internet tunnel needed.

```
Claude Code  ──────────────────→  src/mcp_server.py  →  OneNote
              (direct local connection)
```

### Claude.ai (the web/mobile app)
Claude.ai lives in the cloud. It cannot reach your local PC directly. So we use **ngrok** to create a secure tunnel — a temporary bridge between the internet and your local server.

```
Claude.ai  →  internet  →  ngrok tunnel  →  src/http_mcp_server.py  →  OneNote
```

See `NGROK.md` for a plain English explanation of what ngrok does.

---

## What is a "Tool" in MCP?

When you build an MCP server, you define **tools** — things Claude is allowed to ask the server to do.

SIMON exposes two tools:

| Tool | What it does |
|------|-------------|
| `save_to_onenote` | Saves text content as a new OneNote page |
| `list_notebooks` | Returns a list of your OneNote notebooks |

Claude can only call these two things. It cannot ask SIMON to do anything else.

---

## OAuth — Why Claude.ai Asks You to Sign In

When Claude.ai connects to an MCP server over the internet, it needs to verify that *you* authorised that connection. This is done via **OAuth** — the same "Sign in with Google" style flow you've seen on many websites.

The first time you add SIMON as a connector in Claude.ai:

1. Claude.ai registers itself with SIMON's server
2. Your browser opens an **Approve** page hosted by SIMON
3. You click **Approve**
4. Claude.ai gets a token and uses it for all future requests

This only happens once per session (because the ngrok URL changes on the free plan). With a fixed URL (paid ngrok or Cloudflare), you approve once and never again.

---

## Further Reading

- [MCP official documentation](https://modelcontextprotocol.io)
- [Anthropic MCP announcement](https://www.anthropic.com/news/model-context-protocol)
- [Claude Code MCP guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [FastMCP (the library SIMON uses)](https://github.com/jlowin/fastmcp)

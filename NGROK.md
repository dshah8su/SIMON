# ngrok — Plain English Guide

## What is ngrok?

Your PC is like a house. It has an address on your local street (e.g. `localhost:8000`) that only you and your neighbours (other apps on your PC) can find.

**ngrok is like a postbox at the end of the street** — it gives your house a public address that anyone on the internet can reach, and forwards all mail to your front door.

Without ngrok, Claude.ai (which lives on the internet) has no way to find SIMON (which runs on your PC).

---

## Why Does SIMON Need It?

| Situation | Needs ngrok? |
|-----------|-------------|
| Using SIMON in **Claude Code** (desktop/CLI) | No — Claude Code runs locally on your PC |
| Using SIMON in **Claude.ai** web or mobile app | Yes — Claude.ai is on the internet |

Claude Code and SIMON are both on your PC, so they talk directly. Claude.ai is in the cloud and needs ngrok to reach your PC.

---

## How It Works

```
Your PC running SIMON
  └─ localhost:8000 (only you can see this)
         ↑
      ngrok creates a tunnel
         ↑
  https://abc123.ngrok-free.app  (the whole internet can reach this)
         ↑
  Claude.ai sends requests here → ngrok forwards them to localhost:8000
```

---

## Free Plan vs Paid Plan

This is the most important thing to understand about ngrok for SIMON:

### Free Plan (what you have now)

- ✅ Works perfectly
- ✅ No credit card needed for basic use
- ✅ Unlimited tunnel hours
- ❌ **URL changes every session** — e.g. today it's `abc123.ngrok-free.app`, tomorrow it's `xyz789.ngrok-free.app`
- ❌ Every session: delete old connector in Claude.ai, add new one with new URL

### Paid Plan (~$10/month)

- ✅ Everything above
- ✅ **Fixed static domain** — e.g. `yourname.ngrok.io` forever
- ✅ Set up Claude.ai connector once, never touch it again
- ✅ Session popup disappears — it was only needed because the URL kept changing

### Free Static Domain (check your dashboard)

ngrok sometimes offers one free static domain per account. Check **dashboard.ngrok.com → Cloud Edge → Domains** — if the option is there without requiring payment, claim it. This gives you the same benefit as the paid plan for free.

---

## The Session Popup

Because the free plan URL changes every session, SIMON shows a popup window when you start it. The popup:

- Automatically detects the new ngrok URL
- Shows it ready to copy
- Lists the steps to update Claude.ai

See `SESSION_POPUP.md` for full details.

---

## Cloudflare Tunnel — Free Alternative

[Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) (formerly Argo Tunnel) is a completely free alternative to ngrok:

- No credit card ever required
- Works similarly — creates a public URL that forwards to your local server
- On the free tier, the URL also changes per session (same limitation as ngrok free)
- For a fixed URL, you need a Cloudflare account (free) and a domain name you own

SIMON is planned to support Cloudflare Tunnel as a setup option. For now, ngrok is the default.

---

## Setup Summary

### Already done for you:
- ✅ ngrok installed via `winget`
- ✅ Auth token configured
- ✅ Startup script (`start_simon_ngrok.ps1`) handles everything automatically

### Every session (free plan):
1. Run `start_simon_ngrok.ps1`
2. Copy the URL from the popup
3. Delete old SIMON connector in Claude.ai
4. Add new connector with new URL + `/sse`
5. Click Approve on the browser page

### One-time setup (paid plan or static domain):
1. Get your fixed domain
2. Update `start_simon_ngrok.ps1` — one line change
3. Set up Claude.ai connector once, done forever

---

## Further Reading

- [ngrok documentation](https://ngrok.com/docs)
- [ngrok pricing](https://ngrok.com/pricing)
- [Cloudflare Tunnel documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)

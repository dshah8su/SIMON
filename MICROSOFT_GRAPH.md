# Microsoft Graph API — Plain English Guide

## What is Microsoft Graph?

Think of Microsoft Graph as a **universal remote control for your Microsoft account**.

Your Microsoft account has lots of stuff in it — emails in Outlook, files in OneDrive, calendar events, Teams chats, and yes — your OneNote notebooks. Normally, only Microsoft's own apps can touch that data.

**Microsoft Graph is the official front door** that lets other apps (like SIMON) request access to your data — but only the specific bits you agree to share, and only after you personally approve it.

---

## The Analogy

Imagine a hotel:

- **Your Microsoft account** = your hotel room
- **Microsoft Graph** = the front desk
- **SIMON** = a room service app on your phone
- **Your permission** = you telling the front desk "yes, let this app order food for me"

The room service app never gets your room key. It just gets permission to order food on your behalf, through the front desk. That's exactly how SIMON works with OneNote.

---

## Why Does SIMON Use It?

SIMON needs to:
1. Find your OneNote notebooks
2. Create pages inside them
3. Save your Claude conversations there

There's no other official way to do this. Microsoft Graph is the only approved, secure method for any third-party app to write to OneNote.

---

## What Permissions Does SIMON Request?

SIMON asks for exactly **one permission**:

| Permission | What it allows | What it does NOT allow |
|-----------|---------------|----------------------|
| `Notes.ReadWrite` | Read and write to your OneNote notebooks | Access email, files, calendar, contacts, or anything else |

That's it. No access to your emails, no access to your files, nothing outside OneNote.

You can verify this yourself in your Microsoft account at **myaccount.microsoft.com → Privacy → Apps and services**.

---

## How the Permission Flow Works (First Time Only)

```
You run SIMON for the first time
        ↓
SIMON asks Microsoft: "Can I get permission to access this person's OneNote?"
        ↓
Microsoft sends SIMON a short code (e.g. "SHRKVAJ4")
        ↓
SIMON shows you: "Go to microsoft.com/devicelogin and enter SHRKVAJ4"
        ↓
You open the link, enter the code, sign in with your Microsoft account
        ↓
Microsoft asks you: "Do you want to give SIMON access to your OneNote?" → You click Yes
        ↓
Microsoft gives SIMON a token (like a temporary VIP pass)
        ↓
SIMON saves that token locally on your PC — you won't be asked again for ~90 days
```

After the first time, SIMON silently refreshes the token in the background. You only see the sign-in screen again if you haven't used SIMON in 90 days.

---

## Where is Your Token Stored?

The token is saved in:
```
SIMON/config/token_cache.bin
```

This file **never leaves your machine**. It is excluded from git (listed in `.gitignore`) so it can never accidentally be uploaded to GitHub.

---

## API Calls SIMON Makes

Every time you save to OneNote, SIMON makes these requests behind the scenes:

```
GET  /me/onenote/notebooks              → find your "AI" notebook
POST /me/onenote/notebooks              → create it if it doesn't exist yet
GET  /me/onenote/notebooks/{id}/sections → find the "Claude Conversation" section
POST /me/onenote/notebooks/{id}/sections → create it if needed
POST /me/onenote/sections/{id}/pages    → save the actual content as a new page
```

All requests go to `https://graph.microsoft.com/v1.0/` — Microsoft's official API endpoint.

---

## Is It Safe?

Yes. Here's why:

- **You control the permissions** — you personally approved them and can revoke them any time
- **Minimal access** — only `Notes.ReadWrite`, nothing else
- **No server in the middle** — SIMON runs on your own PC and talks directly to Microsoft
- **Token stored locally** — never uploaded anywhere
- **Open source** — every line of code is visible in this repo

To revoke SIMON's access at any time: **myaccount.microsoft.com → Privacy → Apps and services → SIMON → Remove access**

---

## Further Reading

- [Microsoft Graph overview](https://learn.microsoft.com/en-us/graph/overview)
- [OneNote API documentation](https://learn.microsoft.com/en-us/graph/integrate-with-onenote)
- [Microsoft Graph permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference)

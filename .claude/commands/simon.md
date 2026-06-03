# SIMON — Save to OneNote

Save the last AI response to Microsoft OneNote.

## Trigger
This skill activates when the user types `/simon`, `/simon summarize this`, or simply **SIMON** (any case, with or without slash).

## Usage
- `/simon` — save the last response with section selection
- `/simon summarize this` — summarize first, confirm, then save with section selection

## Workflow — Always Follow This Order

**Step 1 — Call `list_sections` first**
Before saving anything, always call the `list_sections` tool to fetch existing sections in the "AI" notebook. Present them to the user like this:

> Here are your existing sections in OneNote:
> • Claude Conversation
> • Research
> • Code Snippets
>
> Which section should I save this to? You can also type a new name to create one.

**Step 2 — Wait for the user to choose**
- If the user picks an existing section → use that name
- If the user types a new name → use it (it will be created automatically)
- If the user says "default" or doesn't care → use "Claude Conversation"

**Step 3 — Generate a title**
Never leave the title blank. Derive a short descriptive title (max 8 words) from the conversation topic.
Examples: "OneNote Setup Troubleshooting", "Python Async Patterns", "Kivo Mart Website Plan"
Do NOT use timestamps as the title.

**Step 4 — Call `save_to_onenote`**
Call with:
- `content`: the last assistant response (verbatim), or the summary if in summarize mode
- `title`: the descriptive title from Step 3
- `section`: the section chosen in Step 2

Each save creates a **new page** — existing pages are never overwritten.

**Step 5 — Confirm**
Show the user the OneNote link returned. Always confirm with the URL.

---

## Mode 2: `/simon summarize this`

1. Summarize the last assistant response:
   - Short title (max 8 words, from conversation topic)
   - Key points (bullet list, max 5 bullets)
   - 2–3 sentence summary

2. Show the summary and ask: **"Save this to OneNote? (yes / edit / cancel)"**

3. If confirmed → follow the full workflow above (list sections → choose → save)
   If cancelled → respond "Not saved."
   If edit → let the user modify, then follow the workflow.

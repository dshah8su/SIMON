"""
SIMON Session Popup
Shows the current ngrok URL and connector update steps in a clean window.
"""

import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import json


def get_ngrok_url(retries=10) -> str:
    for _ in range(retries):
        try:
            req = urllib.request.Request(
                "http://localhost:4040/api/tunnels",
                headers={"User-Agent": "SIMON/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                for tunnel in data.get("tunnels", []):
                    url = tunnel.get("public_url", "")
                    if url.startswith("https://"):
                        return url
        except Exception:
            pass
        time.sleep(1)
    return ""


def copy_to_clipboard(root, text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()


def build_popup(ngrok_url: str):
    sse_url = f"{ngrok_url}/sse" if ngrok_url else "Could not get URL — is ngrok running?"

    root = tk.Tk()
    root.title("SIMON is Running")
    root.resizable(False, False)
    root.configure(bg="#1e1e2e")

    # Centre on screen
    root.update_idletasks()
    w, h = 480, 420
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    PAD = 20
    BG       = "#1e1e2e"
    CARD     = "#2a2a3e"
    BLUE     = "#4f9cf9"
    GREEN    = "#4ade80"
    TEXT     = "#e2e8f0"
    SUBTEXT  = "#94a3b8"
    DIVIDER  = "#3a3a52"

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = tk.Frame(root, bg=BG)
    hdr.pack(fill="x", padx=PAD, pady=(PAD, 0))

    tk.Label(hdr, text="● SIMON is Running", font=("Segoe UI", 13, "bold"),
             fg=GREEN, bg=BG).pack(side="left")
    tk.Label(hdr, text="Save to OneNote", font=("Segoe UI", 9),
             fg=SUBTEXT, bg=BG).pack(side="right", pady=2)

    tk.Frame(root, height=1, bg=DIVIDER).pack(fill="x", padx=PAD, pady=(10, 0))

    # ── URL card ──────────────────────────────────────────────────────────────
    card = tk.Frame(root, bg=CARD, bd=0, relief="flat")
    card.pack(fill="x", padx=PAD, pady=(14, 0))

    tk.Label(card, text="Connector URL  (add /sse at the end)",
             font=("Segoe UI", 8), fg=SUBTEXT, bg=CARD).pack(anchor="w", padx=14, pady=(10, 2))

    url_row = tk.Frame(card, bg=CARD)
    url_row.pack(fill="x", padx=14, pady=(0, 10))

    url_var = tk.StringVar(value=sse_url)
    url_entry = tk.Entry(url_row, textvariable=url_var, font=("Consolas", 9),
                         fg=BLUE, bg="#12122a", relief="flat",
                         bd=6, readonlybackground="#12122a", state="readonly", width=42)
    url_entry.pack(side="left", ipady=4)

    copied_label = tk.Label(url_row, text="", font=("Segoe UI", 8), fg=GREEN, bg=CARD, width=8)
    copied_label.pack(side="left", padx=(8, 0))

    def on_copy():
        copy_to_clipboard(root, sse_url)
        copied_label.config(text="Copied ✓")
        root.after(2000, lambda: copied_label.config(text=""))

    tk.Button(url_row, text="Copy", font=("Segoe UI", 8, "bold"),
              fg="white", bg=BLUE, relief="flat", bd=0,
              padx=10, pady=4, cursor="hand2",
              command=on_copy).pack(side="left", padx=(6, 0))

    # ── Divider ───────────────────────────────────────────────────────────────
    tk.Frame(root, height=1, bg=DIVIDER).pack(fill="x", padx=PAD, pady=(14, 0))

    # ── Steps ────────────────────────────────────────────────────────────────
    tk.Label(root, text="First time only — set up Claude.ai connector once",
             font=("Segoe UI", 9, "bold"), fg=TEXT, bg=BG).pack(anchor="w", padx=PAD, pady=(12, 4))

    steps = [
        ("1", "Open Claude.ai  →  Settings  →  Integrations / Connectors"),
        ("2", "Click  Add  →  set Name: SIMON"),
        ("3", "Paste the URL above  (ending in /sse)  →  Save"),
        ("4", "A browser tab opens — click  Approve  to authorise"),
        ("5", "Done — this URL is fixed, never needs updating again"),
    ]

    steps_frame = tk.Frame(root, bg=BG)
    steps_frame.pack(fill="x", padx=PAD)

    for _, text in steps:
        row = tk.Frame(steps_frame, bg=BG)
        row.pack(fill="x", pady=0)

        tk.Label(row, text="•", font=("Segoe UI", 9),
                 fg=BLUE, bg=BG).pack(side="left", padx=(0, 6))

        tk.Label(row, text=text, font=("Segoe UI", 8),
                 fg=SUBTEXT, bg=BG, anchor="w").pack(side="left")

    # ── Footer ────────────────────────────────────────────────────────────────
    tk.Frame(root, height=1, bg=DIVIDER).pack(fill="x", padx=PAD, pady=(14, 0))

    footer = tk.Frame(root, bg=BG)
    footer.pack(fill="x", padx=PAD, pady=(10, PAD))

    tk.Label(footer, text="Keep this window open while using SIMON in Claude.ai",
             font=("Segoe UI", 8), fg=SUBTEXT, bg=BG).pack(side="left")

    tk.Button(footer, text="Close", font=("Segoe UI", 8),
              fg=SUBTEXT, bg=CARD, relief="flat", bd=0,
              padx=10, pady=3, cursor="hand2",
              command=root.destroy).pack(side="right")

    root.mainloop()


def main():
    # Show a loading splash while fetching URL
    splash = tk.Tk()
    splash.title("SIMON")
    splash.geometry("300x80")
    splash.resizable(False, False)
    splash.configure(bg="#1e1e2e")
    splash.update_idletasks()
    x = (splash.winfo_screenwidth() - 300) // 2
    y = (splash.winfo_screenheight() - 80) // 2
    splash.geometry(f"300x80+{x}+{y}")
    tk.Label(splash, text="Starting SIMON…", font=("Segoe UI", 11),
             fg="#94a3b8", bg="#1e1e2e").pack(expand=True)
    splash.update()

    ngrok_url = get_ngrok_url()
    splash.destroy()

    if not ngrok_url:
        messagebox.showerror("SIMON", "Could not reach ngrok.\nMake sure ngrok is running on port 8000.")
        sys.exit(1)

    build_popup(ngrok_url)


if __name__ == "__main__":
    main()

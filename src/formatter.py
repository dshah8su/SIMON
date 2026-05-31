"""
SIMON - formatter.py
---------------------
Converts plain text and markdown into the HTML format that OneNote requires.

WHY THIS IS NEEDED:
OneNote does not accept plain text directly — it requires HTML.
This file acts as a translator:
  Plain text / Markdown  →  OneNote-compatible HTML

MARKDOWN SUPPORTED:
  ## Heading          →  <h2>
  ### Subheading      →  <h3>
  **bold**            →  <strong>bold</strong>
  *italic*            →  <em>italic</em>
  `code`              →  <code>code</code>
  ```code block```    →  <pre><code>...</code></pre>
  - bullet            →  <ul><li>
  blank line          →  paragraph break
"""

import html
import re
from datetime import datetime, timezone


class ContentFormatter:
    """Converts content into OneNote-compatible HTML pages."""

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================

    def to_onenote_html(self, title: str, content: str) -> str:
        """
        Builds a complete OneNote HTML page from a title and content string.

        OneNote requires a specific HTML structure:
          <!DOCTYPE html>
          <html>
            <head>
              <title>Page Title</title>
              <meta name="created" content="ISO timestamp" />
            </head>
            <body>
              ... your content ...
            </body>
          </html>

        The content is processed by _markdown_to_html() before being inserted.
        """
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%d %H:%M UTC")  # human-readable date shown on the page
        iso_ts    = now.strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO format required by OneNote's meta tag
        safe_title = html.escape(title or "SIMON Note")  # escape special characters like < > &

        # Convert the markdown content to HTML
        body_html = self._markdown_to_html(content)

        # Assemble the final OneNote HTML page
        return f"""<!DOCTYPE html>
<html>
  <head>
    <title>{safe_title}</title>
    <meta name="created" content="{iso_ts}" />
  </head>
  <body>
    <h1>{safe_title}</h1>
    <p style="color:#888;font-size:12px;">
      <em>Saved by SIMON on {timestamp}</em>
    </p>
    <hr />
    {body_html}
  </body>
</html>"""

    def format_page_title(self, topic: str = "", source: str = "") -> str:
        """
        Generates a readable page title when the user doesn't provide one.

        Examples:
          format_page_title("Python async", "Claude") → "Claude · Python async · 2026-05-30 14:32"
          format_page_title()                          → "SIMON Note · 2026-05-30 14:32"
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        parts = [p for p in [source, topic, now] if p]  # only include non-empty parts
        return " · ".join(parts) if parts else f"SIMON Note · {now}"

    # =========================================================================
    # PRIVATE: MARKDOWN TO HTML CONVERSION
    # =========================================================================

    def _markdown_to_html(self, text: str) -> str:
        """
        Converts markdown-style text to HTML line by line.
        Handles: code blocks, headings, bullet lists, bold, italic, inline code.
        """
        if not text:
            return "<p><em>(no content)</em></p>"

        # Step 1: Convert fenced code blocks first (``` ... ```)
        # These are multi-line so we handle them before splitting into lines
        text = re.sub(
            r"```(?:\w+)?\n(.*?)```",  # matches ```python\n...\n``` or ```\n...\n```
            lambda m: f"<pre><code>{html.escape(m.group(1))}</code></pre>",
            text,
            flags=re.DOTALL,  # DOTALL makes . match newlines too
        )

        # Step 2: Process line by line for headings and list items
        lines      = text.split("\n")
        html_lines = []
        in_ul      = False  # tracks whether we're currently inside a <ul> list

        for line in lines:
            stripped = line.rstrip()

            # Already-converted code block tags — pass through unchanged
            if stripped.startswith("<pre>") or stripped.startswith("</pre>"):
                if in_ul:
                    html_lines.append("</ul>")
                    in_ul = False
                html_lines.append(stripped)
                continue

            # ### Heading (level 3)
            if stripped.startswith("### "):
                if in_ul: html_lines.append("</ul>"); in_ul = False
                html_lines.append(f"<h3>{html.escape(stripped[4:])}</h3>")

            # ## Heading (level 2)
            elif stripped.startswith("## "):
                if in_ul: html_lines.append("</ul>"); in_ul = False
                html_lines.append(f"<h2>{html.escape(stripped[3:])}</h2>")

            # # Heading (level 1) — mapped to h2 since h1 is the page title
            elif stripped.startswith("# "):
                if in_ul: html_lines.append("</ul>"); in_ul = False
                html_lines.append(f"<h2>{html.escape(stripped[2:])}</h2>")

            # - bullet item or * bullet item
            elif re.match(r"^[-*]\s+", stripped):
                item_text = stripped[2:].strip()  # remove the "- " or "* " prefix
                if not in_ul:
                    html_lines.append("<ul>")  # open the list if not already open
                    in_ul = True
                html_lines.append(f"  <li>{self._inline(item_text)}</li>")

            # Blank line — close any open list, add a line break
            elif stripped == "":
                if in_ul:
                    html_lines.append("</ul>")
                    in_ul = False
                html_lines.append("<br/>")

            # Regular paragraph line
            else:
                if in_ul:
                    html_lines.append("</ul>")
                    in_ul = False
                html_lines.append(f"<p>{self._inline(stripped)}</p>")

        # Close any list that was still open at end of content
        if in_ul:
            html_lines.append("</ul>")

        return "\n    ".join(html_lines)

    def _inline(self, text: str) -> str:
        """
        Applies inline formatting to a single line of text.
        Order matters: escape HTML first, then apply markdown patterns.

        **bold**   →  <strong>bold</strong>
        *italic*   →  <em>italic</em>
        `code`     →  <code>code</code>
        """
        # Escape HTML special characters first (&, <, >, etc.)
        text = html.escape(text)

        # **bold** → <strong>bold</strong>
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

        # *italic* → <em>italic</em>  (but not ** which is bold)
        text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)

        # `inline code` → <code>inline code</code>
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)

        return text

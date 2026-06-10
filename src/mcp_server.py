"""
SIMON - mcp_server.py
----------------------
This is the bridge between Claude and OneNote.

WHAT IS MCP?
MCP (Model Context Protocol) is a standard way for Claude to talk to
external tools. By running this server, Claude gains two new abilities:
  1. save_to_onenote — save any text to OneNote
  2. list_notebooks  — see what notebooks you have

HOW IT CONNECTS TO CLAUDE:
This server is registered in Claude Code via:
  claude mcp add simon <python path> <this file path>

When you type /simon in Claude Code, Claude calls save_to_onenote()
through this server, which then calls onenote_client.py to do the actual save.

FLOW:
  User types /simon
       ↓
  Claude calls save_to_onenote(content, title)
       ↓
  This server receives the call
       ↓
  OneNoteClient.save_page() sends it to Microsoft Graph API
       ↓
  Page appears in OneNote
       ↓
  Claude confirms with the OneNote URL
"""

import sys
import os

# Add the src/ folder to Python's path so we can import sibling files
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
from onenote_client import OneNoteClient
from formatter import ContentFormatter
from config import DEFAULT_NOTEBOOK, DEFAULT_SECTION

# ---------------------------------------------------------------------------
# Create the MCP server
# The "instructions" tell Claude how to use this server's tools
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="SIMON",
    instructions=(
        "SIMON saves content to Microsoft OneNote. "
        "Two modes of operation: "
        "(1) EXPLICIT OVERRIDE — if the user names a specific section, use it exactly as given. "
        "Do not call list_sections_with_context. Do not analyze the content. Just save there. "
        "(2) AUTO-ROUTING — if the user gives no section, call list_sections_with_context first, "
        "read the section names and recent page titles, then pick the best-matching existing section. "
        "If no existing section fits, derive a short (2-3 word) name from the topic and create it. "
        "Only ask the user when two sections are genuinely equally close. "
        "Use save_to_onenote to save. Use list_notebooks to show available notebooks. "
        "Always confirm with the returned OneNote URL after saving."
    ),
)

# ---------------------------------------------------------------------------
# Lazy initialization — the OneNote client is only created on first use.
# This avoids triggering the Microsoft sign-in at server startup.
# ---------------------------------------------------------------------------
_client: OneNoteClient | None = None


def _get_client() -> OneNoteClient:
    """Returns the OneNoteClient, creating it on first call."""
    global _client
    if _client is None:
        _client = OneNoteClient()
    return _client


# ---------------------------------------------------------------------------
# TOOL 1: save_to_onenote
# This is the main tool — called when user types /simon
# ---------------------------------------------------------------------------

@mcp.tool()
def save_to_onenote(
    content: str,
    title: str = "",
    notebook: str = DEFAULT_NOTEBOOK,
    section: str = DEFAULT_SECTION,
) -> str:
    """
    Save content to Microsoft OneNote.

    Args:
        content:  The text to save. Supports markdown formatting.
        title:    The page title. A descriptive title is auto-generated if left empty.
        notebook: Which notebook to save into. Defaults to "My Notebook".
        section:  Which section to save into. Defaults to "Claude Conversation".

    Returns:
        A confirmation message with a clickable link to the saved page.
    """
    try:
        formatter = ContentFormatter()

        # If no title was given, generate one with a timestamp
        if not title.strip():
            title = formatter.format_page_title()

        # Save the page using the OneNote client
        result = _get_client().save_page(
            content=content,
            title=title,
            notebook_name=notebook,
            section_name=section,
        )

        # Build a human-readable confirmation message
        web_url    = result.get("oneNoteWebUrl", "")
        client_url = result.get("oneNoteClientUrl", "")

        lines = [
            f"Saved to OneNote!",
            f"Notebook : {result['notebook']}",
            f"Section  : {result['section']}",
            f"Title    : {result['title']}",
        ]
        if web_url:
            lines.append(f"Open in browser : {web_url}")
        if client_url:
            lines.append(f"Open in app     : {client_url}")

        return "\n".join(lines)

    except Exception as exc:
        # Return the error as a string so Claude can show it to the user
        return f"Failed to save to OneNote: {exc}"


# ---------------------------------------------------------------------------
# TOOL 2: list_sections_with_context
# Called before saving — lets Claude see existing sections and recent page
# titles so it can route content to the right section without asking the user.
# ---------------------------------------------------------------------------

@mcp.tool()
def list_sections_with_context(notebook: str = DEFAULT_NOTEBOOK) -> str:
    """
    Lists all sections in a notebook with their 5 most recent page titles.

    Call this BEFORE save_to_onenote to decide which section the content belongs in.
    The recent page titles reveal each section's topic so you can judge whether
    the new content fits an existing section or needs a new one.

    Args:
        notebook: The notebook to inspect. Defaults to the configured default notebook.

    Returns:
        A formatted list of sections and their recent page titles.
    """
    try:
        sections = _get_client().list_sections_with_context(notebook)

        if not sections:
            return (
                f'No sections found in "{notebook}". '
                "A new section will be created on first save."
            )

        lines = [f'Sections in "{notebook}":']
        for sec in sections:
            recent = sec["recent_pages"]
            if recent:
                pages_preview = ", ".join(f'"{t}"' for t in recent)
                lines.append(f'  - {sec["name"]}  (recent pages: {pages_preview})')
            else:
                lines.append(f'  - {sec["name"]}  (no pages yet)')

        return "\n".join(lines)

    except Exception as exc:
        return f"Could not list sections: {exc}"


# ---------------------------------------------------------------------------
# TOOL 3: list_notebooks
# Shows the user what notebooks are available
# ---------------------------------------------------------------------------

@mcp.tool()
def list_notebooks() -> str:
    """
    List all OneNote notebooks in the user's Microsoft account.

    Returns:
        A formatted list of notebook names.
    """
    try:
        notebooks = _get_client().list_notebooks()

        if not notebooks:
            return "No notebooks found. A new one will be created when you first save."

        names = [nb["displayName"] for nb in notebooks]
        lines = ["Your OneNote notebooks:"] + [f"  - {n}" for n in names]
        return "\n".join(lines)

    except Exception as exc:
        return f"Could not list notebooks: {exc}"


# ---------------------------------------------------------------------------
# ENTRY POINT
# When this file is run directly (python mcp_server.py), it starts the server.
# Claude Code launches this automatically when the MCP server is registered.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()

"""
SIMON - mcp_server.py
----------------------
This is the bridge between Claude Code and OneNote.

WHAT IS MCP?
MCP (Model Context Protocol) is a standard way for Claude to talk to
external tools. By running this server, Claude gains three abilities:
  1. list_sections   — show existing sections so user can choose where to save
  2. save_to_onenote — save any text as a new page in a chosen section
  3. list_notebooks  — see what notebooks are available

FLOW:
  User types SIMON or /simon
       ↓
  Claude calls list_sections → shows existing sections to user
       ↓
  User picks a section (or names a new one)
       ↓
  Claude calls save_to_onenote(content, title, section)
       ↓
  OneNoteClient.save_page() sends it to Microsoft Graph API
       ↓
  New page appears in OneNote under the chosen section
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
        "IMPORTANT WORKFLOW: When the user asks to save, ALWAYS call list_sections first "
        "to show them their existing sections, then ask which section to save to (or if they "
        "want a new one). Only call save_to_onenote after the user has chosen a section. "
        "Each save creates a new page — existing pages are never overwritten. "
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
# TOOL 1: list_sections
# Called first so the user can choose where to save
# ---------------------------------------------------------------------------

@mcp.tool()
def list_sections(notebook: str = DEFAULT_NOTEBOOK) -> str:
    """
    List all existing sections in a OneNote notebook.

    Call this BEFORE save_to_onenote so the user can choose which section
    to save to. The user may pick an existing section or type a new name
    to create one automatically.

    Args:
        notebook: The notebook to list sections from. Defaults to "AI".

    Returns:
        A formatted list of section names and a prompt for the user to choose.
    """
    try:
        names = _get_client().list_sections_in_notebook(notebook)
        if not names:
            return f"No sections found in '{notebook}' yet. Type a name to create your first section."
        lines = [f"📑 Sections in '{notebook}':"] + [f"  • {n}" for n in names]
        lines.append("\nWhich section should this be saved to? You can also type a new name to create one.")
        return "\n".join(lines)
    except Exception as exc:
        return f"Could not list sections: {exc}"


# ---------------------------------------------------------------------------
# TOOL 2: save_to_onenote
# Called after the user has chosen a section
# ---------------------------------------------------------------------------

@mcp.tool()
def save_to_onenote(
    content: str,
    title: str = "",
    notebook: str = DEFAULT_NOTEBOOK,
    section: str = DEFAULT_SECTION,
) -> str:
    """
    Save content as a new page in a Microsoft OneNote section.
    Each call creates a brand new page — existing pages are never overwritten.

    Always call list_sections first so the user can choose which section to save to.
    If the user names a section that does not exist, it will be created automatically.

    Args:
        content:  The text to save. Supports markdown formatting.
        title:    Descriptive page title derived from the conversation topic.
        notebook: Which notebook to save into. Defaults to "AI".
        section:  Section chosen by the user. Created automatically if it does not exist.

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
# TOOL 2: list_notebooks
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

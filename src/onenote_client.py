"""
SIMON - onenote_client.py
--------------------------
Talks to Microsoft Graph API to read and write OneNote notebooks.

WHAT THIS FILE DOES:
- Lists your OneNote notebooks
- Finds (or creates) the right notebook and section
- Saves a new page with your content

MICROSOFT GRAPH API ENDPOINTS USED:
  GET  /me/onenote/notebooks                          → list all notebooks
  POST /me/onenote/notebooks                          → create a new notebook
  GET  /me/onenote/notebooks/{id}/sections            → list sections in a notebook
  POST /me/onenote/notebooks/{id}/sections            → create a new section
  POST /me/onenote/sections/{id}/pages                → save a new page (main action)
"""

import requests
from auth import MicrosoftAuth
from config import GRAPH_BASE_URL, DEFAULT_NOTEBOOK, DEFAULT_SECTION


class OneNoteClient:
    """
    High-level interface to OneNote via Microsoft Graph.
    Handles authentication automatically on first use.
    """

    def __init__(self):
        # MicrosoftAuth handles the sign-in and token management
        self._auth = MicrosoftAuth()

    # =========================================================================
    # PUBLIC METHODS — these are what mcp_server.py and http_server.py call
    # =========================================================================

    def list_notebooks(self) -> list[dict]:
        """
        Returns a list of all OneNote notebooks in the user's account.
        Each item has: { "id": "...", "displayName": "My Notebook" }
        """
        data = self._get("/me/onenote/notebooks", params={"$select": "id,displayName"})
        return data.get("value", [])

    def list_sections_in_notebook(self, notebook_name: str = DEFAULT_NOTEBOOK) -> list[str]:
        """
        Returns the display names of all sections in a given notebook.
        Creates the notebook first if it doesn't exist yet.
        """
        notebook_id = self._get_or_create_notebook(notebook_name)
        sections = self._list_sections(notebook_id)
        return [s["displayName"] for s in sections]

    def save_page(
        self,
        content: str,
        title: str,
        notebook_name: str = DEFAULT_NOTEBOOK,
        section_name: str = DEFAULT_SECTION,
    ) -> dict:
        """
        Saves content as a new page in OneNote.

        Steps:
          1. Find the notebook by name (create it if it doesn't exist)
          2. Find the section by name inside that notebook (create if needed)
          3. Convert content to OneNote HTML format
          4. POST the page to the Microsoft Graph API

        Returns a dict with:
          - oneNoteWebUrl    → open in browser
          - oneNoteClientUrl → open in OneNote app
          - title, notebook, section
        """
        # Step 1: Get or create the target notebook
        notebook_id = self._get_or_create_notebook(notebook_name)

        # Step 2: Get or create the target section inside that notebook
        section_id = self._get_or_create_section(notebook_id, section_name)

        # Step 3: Convert the plain text / markdown content into OneNote HTML
        from formatter import ContentFormatter
        html = ContentFormatter().to_onenote_html(title=title, content=content)

        # Step 4: POST the HTML page to OneNote
        response = self._post_page(section_id, html)

        # Extract the links from the response
        links = response.get("links", {})
        return {
            "oneNoteWebUrl":    links.get("oneNoteWebUrl",    {}).get("href", ""),
            "oneNoteClientUrl": links.get("oneNoteClientUrl", {}).get("href", ""),
            "title":    response.get("title", title),
            "notebook": notebook_name,
            "section":  section_name,
        }

    # =========================================================================
    # NOTEBOOK HELPERS
    # =========================================================================

    def _get_or_create_notebook(self, name: str) -> str:
        """
        Looks for a notebook with the given name.
        If found → returns its ID.
        If not found → creates it and returns the new ID.
        """
        # Search through existing notebooks (case-insensitive match)
        for nb in self.list_notebooks():
            if nb["displayName"].lower() == name.lower():
                return nb["id"]

        # Not found — create a new notebook with this name
        created = self._post(
            "/me/onenote/notebooks",
            json={"displayName": name},
        )
        return created["id"]

    # =========================================================================
    # SECTION HELPERS
    # =========================================================================

    def _list_sections(self, notebook_id: str) -> list[dict]:
        """
        Returns all sections inside a given notebook.
        Each item has: { "id": "...", "displayName": "Quick Notes" }
        """
        data = self._get(
            f"/me/onenote/notebooks/{notebook_id}/sections",
            params={"$select": "id,displayName"},
        )
        return data.get("value", [])

    def _get_or_create_section(self, notebook_id: str, name: str) -> str:
        """
        Looks for a section with the given name inside a notebook.
        If found → returns its ID.
        If not found → creates it and returns the new ID.
        """
        # Search through existing sections (case-insensitive match)
        for sec in self._list_sections(notebook_id):
            if sec["displayName"].lower() == name.lower():
                return sec["id"]

        # Not found — create a new section
        created = self._post(
            f"/me/onenote/notebooks/{notebook_id}/sections",
            json={"displayName": name},
        )
        return created["id"]

    # =========================================================================
    # PAGE CREATION
    # =========================================================================

    def _post_page(self, section_id: str, html: str) -> dict:
        """
        POSTs an HTML page to OneNote inside the given section.
        OneNote requires the content to be sent as text/html (not JSON).
        """
        url = f"{GRAPH_BASE_URL}/me/onenote/sections/{section_id}/pages"
        headers = {
            "Authorization": f"Bearer {self._auth.get_token()}",
            "Content-Type": "text/html",  # OneNote pages are sent as raw HTML
        }
        resp = requests.post(url, headers=headers, data=html.encode("utf-8"), timeout=30)
        self._raise_for_status(resp)
        return resp.json()

    # =========================================================================
    # HTTP HELPER METHODS
    # =========================================================================

    def _headers(self) -> dict:
        """
        Returns the Authorization header needed for every Graph API call.
        The Bearer token proves SIMON has permission to access the account.
        """
        return {
            "Authorization": f"Bearer {self._auth.get_token()}",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        """Sends a GET request to Microsoft Graph and returns the JSON response."""
        url = f"{GRAPH_BASE_URL}{path}"
        resp = requests.get(url, headers=self._headers(), params=params, timeout=15)
        self._raise_for_status(resp)
        return resp.json()

    def _post(self, path: str, json: dict) -> dict:
        """Sends a POST request to Microsoft Graph and returns the JSON response."""
        url = f"{GRAPH_BASE_URL}{path}"
        resp = requests.post(url, headers=self._headers(), json=json, timeout=15)
        self._raise_for_status(resp)
        return resp.json()

    @staticmethod
    def _raise_for_status(resp: requests.Response) -> None:
        """
        Checks if the API response was successful (200 or 201).
        If not, raises a clear error message explaining what went wrong.
        """
        if resp.status_code not in (200, 201):
            try:
                detail = resp.json().get("error", {}).get("message", resp.text)
            except Exception:
                detail = resp.text
            raise RuntimeError(
                f"Microsoft Graph API error {resp.status_code}: {detail}"
            )

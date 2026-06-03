"""
SIMON - HTTP MCP Server with OAuth
Runs SIMON tools over SSE with a built-in OAuth 2.0 server for Claude.ai.

Start via the startup script:
  powershell -ExecutionPolicy Bypass -File start_simon_ngrok.ps1

Or manually:
  python src/http_mcp_server.py --public-url https://xxxx.ngrok-free.app
"""

import sys
import os
import secrets
import time
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from pydantic import AnyUrl
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import (
    OAuthAuthorizationServerProvider,
    OAuthClientInformationFull,
    AuthorizationParams,
    AuthorizationCode,
    AccessToken,
    OAuthToken,
    construct_redirect_uri,
)
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions

from onenote_client import OneNoteClient
from formatter import ContentFormatter
from config import DEFAULT_NOTEBOOK, DEFAULT_SECTION, HTTP_HOST, HTTP_PORT

# ── CLI args ──────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--public-url", default=f"http://localhost:{HTTP_PORT}",
                    help="Public URL (ngrok URL) for OAuth redirects")
args, _ = parser.parse_known_args()
PUBLIC_URL = args.public_url.rstrip("/")

# ── In-memory OAuth stores (personal use, resets on restart) ──────────────────
_clients: dict[str, OAuthClientInformationFull] = {}
_sessions: dict[str, dict] = {}      # session_id -> {client, params}
_auth_codes: dict[str, AuthorizationCode] = {}
_tokens: dict[str, AccessToken] = {}


class SIMONOAuthProvider(OAuthAuthorizationServerProvider):

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return _clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        _clients[client_info.client_id] = client_info

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        session_id = secrets.token_urlsafe(16)
        _sessions[session_id] = {"client": client, "params": params}
        return f"{PUBLIC_URL}/approve?session={session_id}"

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, code: str
    ) -> AuthorizationCode | None:
        return _auth_codes.get(code)

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, code: AuthorizationCode
    ) -> OAuthToken:
        _auth_codes.pop(code.code, None)
        token_str = secrets.token_urlsafe(32)
        _tokens[token_str] = AccessToken(
            token=token_str,
            client_id=client.client_id,
            scopes=code.scopes,
            expires_at=None,
            subject=code.subject,
        )
        return OAuthToken(
            access_token=token_str,
            token_type="Bearer",
            scope=" ".join(code.scopes) if code.scopes else None,
        )

    async def exchange_refresh_token(self, client, refresh_token, scopes):
        raise NotImplementedError("Refresh tokens not supported")

    async def load_refresh_token(self, client, token):
        return None

    async def load_access_token(self, token: str) -> AccessToken | None:
        return _tokens.get(token)

    async def revoke_token(self, token: str, token_type_hint: str | None = None) -> None:
        _tokens.pop(token, None)


# ── MCP Server ────────────────────────────────────────────────────────────────
mcp = FastMCP(
    name="SIMON",
    instructions=(
        "SIMON saves content to Microsoft OneNote. "
        "IMPORTANT WORKFLOW: When the user asks to save, ALWAYS call list_sections first "
        "to show them their existing sections, then ask which section to save to (or if they "
        "want a new one). Only call save_to_onenote after the user has chosen a section. "
        "Each save creates a new page in the chosen section. "
        "Always confirm with the returned OneNote URL after saving."
    ),
    auth_server_provider=SIMONOAuthProvider(),
    auth=AuthSettings(
        issuer_url=PUBLIC_URL,
        resource_server_url=PUBLIC_URL,
        client_registration_options=ClientRegistrationOptions(enabled=True),
    ),
    host=HTTP_HOST,
    port=HTTP_PORT,
)

_onenote: OneNoteClient | None = None


def _get_client() -> OneNoteClient:
    global _onenote
    if _onenote is None:
        _onenote = OneNoteClient()
    return _onenote


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_sections(notebook: str = DEFAULT_NOTEBOOK) -> str:
    """
    List all existing sections in a OneNote notebook.

    Call this BEFORE save_to_onenote to show the user their available sections
    so they can choose where to save. The user may pick an existing section or
    provide a new name to create one.

    Args:
        notebook: The notebook to list sections from. Defaults to "AI".

    Returns:
        A formatted list of section names, or a message if none exist yet.
    """
    try:
        names = _get_client().list_sections_in_notebook(notebook)
        if not names:
            return f"No sections found in '{notebook}' yet. Type a name to create your first section."
        lines = [f"📑 Sections in '{notebook}':"] + [f"  • {n}" for n in names]
        lines.append("\nWhich section should this be saved to? You can also type a new name to create one.")
        return "\n".join(lines)
    except Exception as exc:
        return f"❌ Could not list sections: {exc}"


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
        content:  The text to save (plain text or markdown).
        title:    Descriptive page title derived from the conversation topic.
        notebook: OneNote notebook name. Defaults to "AI".
        section:  Section chosen by the user. Created automatically if it does not exist.
    """
    try:
        formatter = ContentFormatter()
        if not title.strip():
            title = formatter.format_page_title()
        result = _get_client().save_page(
            content=content, title=title,
            notebook_name=notebook, section_name=section,
        )
        web_url    = result.get("oneNoteWebUrl", "")
        client_url = result.get("oneNoteClientUrl", "")
        lines = [
            "✅ Saved to OneNote!",
            f"📓 Notebook : {result['notebook']}",
            f"📑 Section  : {result['section']}",
            f"📄 Title    : {result['title']}",
        ]
        if web_url:    lines.append(f"🌐 Open web : {web_url}")
        if client_url: lines.append(f"🖥  Open app : {client_url}")
        return "\n".join(lines)
    except Exception as exc:
        return f"❌ Failed to save to OneNote: {exc}"


@mcp.tool()
def list_notebooks() -> str:
    """List all OneNote notebooks available in the user's Microsoft account."""
    try:
        notebooks = _get_client().list_notebooks()
        if not notebooks:
            return "No notebooks found. A new one will be created when you first save."
        names = [nb["displayName"] for nb in notebooks]
        return "\n".join(["📚 Your OneNote notebooks:"] + [f"  • {n}" for n in names])
    except Exception as exc:
        return f"❌ Could not list notebooks: {exc}"


# ── Custom /register — overrides SDK's strict grant_type validation ───────────
# Claude.ai only sends grant_types=["authorization_code"] but the SDK requires
# refresh_token too. This handler accepts whatever Claude.ai sends.

@mcp.custom_route("/register", methods=["POST"])
async def register(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid_request"}, status_code=400)

    client_id = secrets.token_urlsafe(16)
    raw_uris = body.get("redirect_uris") or []

    try:
        parsed_uris = [AnyUrl(u) for u in raw_uris]
    except Exception:
        return JSONResponse({"error": "invalid_client_metadata",
                             "error_description": "invalid redirect_uris"}, status_code=400)

    _clients[client_id] = OAuthClientInformationFull(
        client_id=client_id,
        redirect_uris=parsed_uris,
        grant_types=body.get("grant_types") or ["authorization_code"],
        response_types=body.get("response_types") or ["code"],
        token_endpoint_auth_method=body.get("token_endpoint_auth_method") or "none",
        client_name=body.get("client_name"),
    )

    return JSONResponse({
        "client_id": client_id,
        "client_id_issued_at": int(time.time()),
        "redirect_uris": raw_uris,
        "grant_types": _clients[client_id].grant_types,
        "response_types": _clients[client_id].response_types,
        "token_endpoint_auth_method": _clients[client_id].token_endpoint_auth_method or "none",
    }, status_code=201)


# ── OAuth approval page ───────────────────────────────────────────────────────

@mcp.custom_route("/approve", methods=["GET", "POST"])
async def approve(request: Request) -> HTMLResponse | RedirectResponse:
    if request.method == "GET":
        session_id = request.query_params.get("session", "")
        if session_id not in _sessions:
            return HTMLResponse("<h1>Invalid or expired session</h1>", status_code=400)
        client = _sessions[session_id]["client"]
        return HTMLResponse(f"""<!DOCTYPE html>
<html>
<head><title>SIMON Authorization</title></head>
<body style="font-family:sans-serif;max-width:420px;margin:80px auto;text-align:center;padding:24px">
  <h2 style="color:#0078d4">SIMON &mdash; Save to OneNote</h2>
  <p>Claude.ai is requesting permission to use SIMON to save your conversations to Microsoft OneNote.</p>
  <form method="post">
    <input type="hidden" name="session" value="{session_id}">
    <button type="submit"
      style="padding:12px 32px;background:#0078d4;color:white;border:none;border-radius:6px;font-size:16px;cursor:pointer">
      Approve
    </button>
  </form>
  <p style="color:#aaa;font-size:12px;margin-top:24px">Client: {client.client_id}</p>
</body>
</html>""")

    # POST — user clicked Approve
    form = await request.form()
    session_id = str(form.get("session", ""))
    if session_id not in _sessions:
        return HTMLResponse("<h1>Invalid or expired session</h1>", status_code=400)

    session = _sessions.pop(session_id)
    client: OAuthClientInformationFull = session["client"]
    params: AuthorizationParams = session["params"]

    code = secrets.token_urlsafe(32)
    _auth_codes[code] = AuthorizationCode(
        code=code,
        scopes=params.scopes or [],
        expires_at=time.time() + 300,
        client_id=client.client_id,
        code_challenge=params.code_challenge,
        redirect_uri=params.redirect_uri,
        redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
        resource=params.resource,
    )

    redirect_url = construct_redirect_uri(str(params.redirect_uri), code=code, state=params.state)
    return RedirectResponse(redirect_url, status_code=302)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nSIMON HTTP MCP server")
    print(f"  Public URL : {PUBLIC_URL}")
    print(f"  SSE endpoint : {PUBLIC_URL}/sse")
    print(f"  OAuth approval : {PUBLIC_URL}/approve\n")
    mcp.run(transport="sse")

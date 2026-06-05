"""
SIMON - auth.py
---------------
Handles signing in to your Microsoft account so SIMON can access OneNote.

HOW SIGN-IN WORKS (Device Code Flow):
1. SIMON asks Microsoft for a short code (like "SHRKVAJ4")
2. You go to https://microsoft.com/link and enter that code
3. You sign in with your Microsoft account in the browser
4. Microsoft gives SIMON a token (a digital key) to access OneNote on your behalf
5. That token is saved locally so you only need to do this once (~90 days)

After the first sign-in, SIMON silently refreshes the token in the background.
"""

import sys
import msal
from pathlib import Path

# Import settings from config.py
from config import AZURE_CLIENT_ID, AZURE_TENANT_ID, GRAPH_SCOPES, TOKEN_CACHE_PATH


class MicrosoftAuth:
    """
    Manages the Microsoft OAuth login process.
    Call get_token() to get a valid access token for the Graph API.
    """

    def __init__(self):
        # Check that the Azure Client ID has been set in .env
        # Without this, we can't identify which app is asking for access
        if not AZURE_CLIENT_ID:
            raise RuntimeError(
                "AZURE_CLIENT_ID is not set.\n"
                "Open .env and paste your Azure App's Client ID.\n"
                "See README.md for step-by-step instructions."
            )

        # Load any previously saved token from disk
        self._cache = self._load_cache()

        # Create the MSAL app client
        # PublicClientApplication = an app that runs on the user's device (no server secret needed)
        # authority = the Microsoft login endpoint for the account type
        self._app = msal.PublicClientApplication(
            client_id=AZURE_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{AZURE_TENANT_ID}",
            token_cache=self._cache,
        )

    # -------------------------------------------------------------------------
    # PUBLIC METHOD — this is what the rest of SIMON calls
    # -------------------------------------------------------------------------

    def get_token(self) -> str:
        """
        Returns a valid Bearer token for Microsoft Graph API.
        - If a cached token exists and is still valid → returns it silently
        - If no cached token → starts the device code sign-in flow
        """
        token = self._try_silent_refresh()
        if token:
            return token

        # No valid cached token found — ask the user to sign in
        return self._start_device_code_flow()

    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------

    def _try_silent_refresh(self) -> str | None:
        """
        Tries to get a token silently using the saved refresh token.
        Returns the access token string if successful, or None if sign-in is needed.
        """
        # Check if there are any saved accounts in the token cache
        accounts = self._app.get_accounts()
        if not accounts:
            return None  # No saved accounts — need to sign in

        # Try to get a fresh access token using the saved refresh token
        result = self._app.acquire_token_silent(
            scopes=GRAPH_SCOPES,
            account=accounts[0],  # use the first (and usually only) saved account
        )

        if result and "access_token" in result:
            self._save_cache()  # update the cache with the refreshed token
            return result["access_token"]

        return None  # Silent refresh failed — need to sign in again

    def _start_device_code_flow(self) -> str:
        """
        Starts the device code sign-in flow.
        Prints a URL and a code for the user to enter in their browser.
        Waits until the user completes sign-in.
        """
        # Ask Microsoft for a device code
        flow = self._app.initiate_device_flow(scopes=GRAPH_SCOPES)

        if "user_code" not in flow:
            raise RuntimeError(
                f"Could not start sign-in: {flow.get('error_description', 'Unknown error')}"
            )

        # Show the user what to do
        print("\n" + "=" * 60, flush=True)
        print("  SIMON needs permission to access your OneNote.", flush=True)
        print("=" * 60, flush=True)
        print(f"\n  1. Open this URL in your browser:", flush=True)
        print(f"     {flow['verification_uri']}", flush=True)
        print(f"\n  2. Enter this code: {flow['user_code']}", flush=True)
        print(f"\n  3. Sign in with your Microsoft account.", flush=True)
        print(f"\n  Waiting for you to authenticate ...\n", flush=True)

        # This line blocks (waits) until the user completes sign-in in the browser
        result = self._app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise RuntimeError(f"Authentication failed: {error}")

        # Save the token so the user doesn't need to sign in next time
        self._save_cache()
        print("  [OK] Authentication successful! SIMON is now connected to OneNote.\n", flush=True)
        return result["access_token"]

    # -------------------------------------------------------------------------
    # TOKEN CACHE — saves and loads the token from disk
    # -------------------------------------------------------------------------

    def _load_cache(self) -> msal.SerializableTokenCache:
        """
        Loads the saved token from the local cache file.
        If no cache file exists yet, returns an empty cache.
        """
        cache = msal.SerializableTokenCache()
        if TOKEN_CACHE_PATH.exists():
            cache.deserialize(TOKEN_CACHE_PATH.read_text(encoding="utf-8"))
        return cache

    def _save_cache(self) -> None:
        """
        Saves the current token to disk so it can be reused next time.
        Only writes if the cache actually changed (has_state_changed check).
        """
        if self._cache.has_state_changed:
            TOKEN_CACHE_PATH.write_text(
                self._cache.serialize(),
                encoding="utf-8",
            )

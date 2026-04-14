"""
Self-contained OAuth 2.1 for Heptabase MCP.

Handles the full OAuth lifecycle independently — no Hermes dependency.
Falls back to Hermes tokens if available (backward compatible).

Token resolution order:
  1. ~/.zk-agent/tokens/heptabase.json (own)
  2. ~/.hermes/mcp-tokens/heptabase.json (Hermes fallback)
  3. None → triggers OAuth browser flow
"""

import base64
import json
import os
import socket
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken

HEPTABASE_MCP_URL = "https://api.heptabase.com/mcp"
OWN_TOKEN_DIR = Path.home() / ".zk-agent" / "tokens"
HERMES_TOKEN_DIR = Path.home() / ".hermes" / "mcp-tokens"


# ── Token Storage ──────────────────────────────────────────────────

class ZKAgentTokenStorage(TokenStorage):
    """File-based token storage with Hermes fallback."""

    def __init__(self):
        OWN_TOKEN_DIR.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> dict | None:
        if path.exists():
            return json.loads(path.read_text())
        return None

    def _write_json(self, path: Path, data: dict):
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data))
        os.chmod(tmp, 0o600)
        tmp.rename(path)

    async def get_tokens(self) -> OAuthToken | None:
        # Own tokens first
        data = self._read_json(OWN_TOKEN_DIR / "heptabase.json")
        if data:
            return OAuthToken(**data)
        # Hermes fallback
        data = self._read_json(HERMES_TOKEN_DIR / "heptabase.json")
        if data:
            return OAuthToken(**data)
        return None

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self._write_json(OWN_TOKEN_DIR / "heptabase.json", tokens.model_dump(exclude_none=True))

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        data = self._read_json(OWN_TOKEN_DIR / "heptabase.client.json")
        if data:
            return OAuthClientInformationFull(**data)
        data = self._read_json(HERMES_TOKEN_DIR / "heptabase.client.json")
        if data:
            return OAuthClientInformationFull(**data)
        return None

    async def set_client_info(self, info: OAuthClientInformationFull) -> None:
        self._write_json(OWN_TOKEN_DIR / "heptabase.client.json", info.model_dump(exclude_none=True))


# ── OAuth Callback Server ──────────────────────────────────────────

_callback_result: dict = {}


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)
        if "code" in params:
            _callback_result["code"] = params["code"][0]
            _callback_result["state"] = params.get("state", [""])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Authorized! You can close this tab.</h2>")

    def log_message(self, format, *args):
        pass  # suppress HTTP log noise


def _start_callback_server(port: int) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", port), _CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ── Public API ─────────────────────────────────────────────────────

def get_stored_token() -> str | None:
    """Get a stored access token (own or Hermes), or None."""
    for path in [OWN_TOKEN_DIR / "heptabase.json", HERMES_TOKEN_DIR / "heptabase.json"]:
        if path.exists():
            data = json.loads(path.read_text())
            token = data.get("access_token")
            if token:
                return token
    return None


def get_token_status() -> dict:
    """Check token status: valid, source, expiry."""
    for name, dir_ in [("zk-agent", OWN_TOKEN_DIR), ("hermes", HERMES_TOKEN_DIR)]:
        path = dir_ / "heptabase.json"
        if path.exists():
            data = json.loads(path.read_text())
            token = data.get("access_token", "")
            # Try to decode JWT exp claim
            expires_at = None
            try:
                payload = token.split(".")[1]
                payload += "=" * (4 - len(payload) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(payload))
                expires_at = decoded.get("exp")
            except Exception:
                pass
            return {"valid": bool(token), "source": name, "expires_at": expires_at}
    return {"valid": False, "source": None, "expires_at": None}


def build_oauth_provider(callback_port: int) -> OAuthClientProvider:
    """Build an OAuthClientProvider for Heptabase MCP."""
    storage = ZKAgentTokenStorage()
    client_metadata = OAuthClientMetadata(
        redirect_uris=[f"http://127.0.0.1:{callback_port}/callback"],
        grant_types=["authorization_code", "refresh_token"],
        response_types=["code"],
        token_endpoint_auth_method="none",
        scope="openid profile email space:read space:write",
    )

    async def redirect_handler(url: str) -> None:
        print(f"\nOpening browser for Heptabase authorization...", flush=True)
        print(f"If browser doesn't open, visit: {url}\n", flush=True)
        webbrowser.open(url)

    async def callback_handler() -> tuple[str, str | None]:
        import asyncio
        for _ in range(600):  # 5 min timeout
            if "code" in _callback_result:
                code = _callback_result.pop("code")
                state = _callback_result.pop("state", None)
                return code, state
            await asyncio.sleep(0.5)
        raise TimeoutError("OAuth callback timed out after 5 minutes")

    return OAuthClientProvider(
        server_url=HEPTABASE_MCP_URL,
        client_metadata=client_metadata,
        storage=storage,
        redirect_handler=redirect_handler,
        callback_handler=callback_handler,
    )

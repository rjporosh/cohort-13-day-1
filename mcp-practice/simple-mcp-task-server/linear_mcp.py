"""
Linear MCP Client — manual OAuth 2.1 + PKCE, standalone.
=========================================================
FINAL POLISHED VERSION — fully working.

What this does:
1. OAuth 2.1 + PKCE flow with Linear (browser opens ONLY the first time).
2. Tokens + client registration cached in ~/.linear_mcp_state.json,
   so later runs connect instantly without the browser.
3. Connects to Linear's MCP server via Streamable HTTP.
4. Lists all available MCP tools.
5. Calls `list_issues` and prints your Linear issues in a clean format.

Why manual OAuth instead of the SDK's OAuthClientProvider:
The SDK was sending client credentials in TWO ways at once
(Basic header + body), which Linear rejects with:
"Client must not use multiple authentication methods".
This implementation uses EXACTLY ONE method, guaranteed.

Run:
    mcp-env/bin/python linear_mcp.py

Reset cached credentials (forces browser login again):
    rm ~/.linear_mcp_state.json
"""

import asyncio
import base64
import hashlib
import json
import secrets
import time
import traceback
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import httpx2

from mcp import Client
from mcp.client.streamable_http import streamable_http_client


# ============================================================
# Configuration — Linear MCP
# ============================================================

MCP_SERVER_URL = "https://mcp.linear.app/mcp"

REDIRECT_URI = "http://localhost:3030/callback"
CALLBACK_HOST = "127.0.0.1"
CALLBACK_PORT = 3030

STATE_FILE = Path.home() / ".linear_mcp_state.json"

FALLBACK_ENDPOINTS = {
    "registration_endpoint": "https://mcp.linear.app/oauth/register",
    "authorization_endpoint": "https://mcp.linear.app/oauth/authorize",
    "token_endpoint": "https://mcp.linear.app/oauth/token",
}
FALLBACK_SCOPES = "read write"

AUTH_TIMEOUT_SECONDS = 300

try:
    MCP_HTTP_TIMEOUT = httpx2.Timeout(600.0, connect=10.0)
except Exception:
    MCP_HTTP_TIMEOUT = 30.0


# ============================================================
# State helpers (token cache on disk)
# ============================================================

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception as exc:
            print(f"[State] Could not read {STATE_FILE}: {exc}")
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))
    print(f"[State] Saved: {STATE_FILE}")


def clear_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()
        print("[State] Cleared stored credentials.")


# ============================================================
# PKCE helpers
# ============================================================

def make_pkce():
    verifier = secrets.token_urlsafe(64)[:128]
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge


# ============================================================
# Local OAuth Callback Server
# ============================================================

class OAuthCallbackServer:

    def __init__(
        self,
        host: str = CALLBACK_HOST,
        port: int = CALLBACK_PORT,
    ):
        self.host = host
        self.port = port

        self.server = None
        self.callback_future = None

    async def start(self):
        """
        Start a tiny local HTTP server.

        Browser will redirect to:

        http://localhost:3030/callback?code=...&state=...
        """

        self.callback_future = asyncio.get_running_loop().create_future()

        self.server = await asyncio.start_server(
            self._handle_connection,
            self.host,
            self.port,
        )

        print()
        print("=" * 70)
        print("LOCAL OAUTH CALLBACK SERVER")
        print("=" * 70)
        print(
            f"Listening on http://localhost:{self.port}/callback"
        )
        print()

    async def _handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        """
        Receive the HTTP request sent by the browser.
        """

        try:
            # Read HTTP request line.
            request_line = await reader.readline()

            if not request_line:
                return

            request_line = request_line.decode(
                "utf-8",
                errors="replace",
            ).strip()

            print()
            print("[OAuth] Browser connected to local callback.")
            print("[OAuth] Request:", request_line)

            # Read remaining HTTP headers.
            while True:
                line = await reader.readline()

                if not line or line in (b"\r\n", b"\n"):
                    break

            parts = request_line.split()

            if len(parts) < 2:
                return

            request_target = parts[1]

            parsed = urlparse(request_target)

            if parsed.path != "/callback":
                await self._send_response(
                    writer,
                    "Not Found",
                    status="404 Not Found",
                )
                return

            # Reconstruct callback URL.
            callback_url = (
                f"http://localhost:{self.port}"
                f"{request_target}"
            )

            # Parse query parameters.
            params = parse_qs(parsed.query)

            print()
            print("=" * 70)
            print("OAUTH CALLBACK RECEIVED")
            print("=" * 70)

            if "error" in params:

                error_message = (
                    f"OAuth error: {params['error'][0]}"
                )

                print(error_message)

                if not self.callback_future.done():
                    self.callback_future.set_exception(
                        RuntimeError(error_message)
                    )

                await self._send_response(
                    writer,
                    """
                    <html>
                    <body>
                        <h2>OAuth authorization failed.</h2>
                        <p>You can close this browser tab.</p>
                    </body>
                    </html>
                    """,
                )

                return

            if "code" not in params:

                error_message = (
                    "Authorization code was not found "
                    "in callback URL."
                )

                print(error_message)

                if not self.callback_future.done():
                    self.callback_future.set_exception(
                        RuntimeError(error_message)
                    )

                await self._send_response(
                    writer,
                    """
                    <html>
                    <body>
                        <h2>Authorization code not found.</h2>
                        <p>You can close this browser tab.</p>
                    </body>
                    </html>
                    """,
                )

                return

            print("[OAuth] Authorization code received.")
            print("[OAuth] No terminal copy/paste required.")

            # Give the URL to the waiting coroutine.
            if not self.callback_future.done():
                self.callback_future.set_result(
                    callback_url
                )

            # Tell browser everything worked.
            await self._send_response(
                writer,
                """
                <html>
                <head>
                    <title>Linear OAuth</title>
                </head>
                <body>
                    <h2>Linear authorization successful!</h2>
                    <p>
                        You can close this browser tab and
                        return to the terminal.
                    </p>
                </body>
                </html>
                """,
            )

        except Exception as exc:

            print()
            print("[OAuth callback server error]")
            print(exc)

            if (
                self.callback_future is not None
                and not self.callback_future.done()
            ):
                self.callback_future.set_exception(exc)

        finally:

            writer.close()

            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def _send_response(
        self,
        writer: asyncio.StreamWriter,
        body: str,
        status: str = "200 OK",
    ):
        body_bytes = body.encode("utf-8")

        response = (
            f"HTTP/1.1 {status}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("utf-8") + body_bytes

        writer.write(response)

        await writer.drain()

    async def wait_for_callback(self) -> str:
        """
        Wait until the browser redirects to localhost.
        """

        if self.callback_future is None:
            raise RuntimeError(
                "OAuth callback server has not been started."
            )

        return await self.callback_future

    async def stop(self):
        """
        Stop the local callback server.
        """

        if self.server is not None:

            self.server.close()

            await self.server.wait_closed()

            self.server = None

            print()
            print("[OAuth] Local callback server stopped.")


# ============================================================
# OAuth discovery / registration / token exchange (manual)
# ============================================================

async def discover_endpoints(http) -> dict:
    """
    Discover OAuth endpoints from .well-known metadata,
    with hardcoded Linear fallbacks.
    """

    endpoints = dict(FALLBACK_ENDPOINTS)
    scopes = FALLBACK_SCOPES
    resource = MCP_SERVER_URL

    try:
        resp = await http.get(
            "https://mcp.linear.app/.well-known/"
            "oauth-protected-resource/mcp"
        )

        if resp.status_code == 200:
            meta = resp.json()

            resource = meta.get("resource") or resource

            supported = meta.get("scopes_supported")
            if supported:
                scopes = " ".join(supported)

            servers = meta.get("authorization_servers") or []

            for auth_server in servers:
                base = str(auth_server).rstrip("/")

                for well_known in (
                    f"{base}/.well-known/oauth-authorization-server",
                    f"{base}/.well-known/openid-configuration",
                ):
                    try:
                        as_resp = await http.get(well_known)
                    except Exception:
                        continue

                    if as_resp.status_code == 200:
                        as_meta = as_resp.json()

                        for key in endpoints:
                            if as_meta.get(key):
                                endpoints[key] = as_meta[key]

                        break
                break

        print("[Discovery] endpoints:",
              json.dumps(endpoints, indent=2))
        print("[Discovery] scopes:", scopes)

    except Exception as exc:
        print(
            "[Discovery] Metadata discovery failed "
            f"({exc}); using fallback endpoints."
        )

    return {
        "endpoints": endpoints,
        "scopes": scopes,
        "resource": resource,
    }


def build_client_auth(client_info: dict, data: dict):
    """
    Attach client credentials using EXACTLY ONE method:

    - client_secret_post  -> client_id + client_secret in body
    - client_secret_basic -> HTTP Basic header, no secret in body
    - none / public       -> client_id only in body (+ PKCE)

    This is the fix for Linear's
    "Client must not use multiple authentication methods".
    """

    method = (
        client_info.get("token_endpoint_auth_method")
        or "client_secret_post"
    )

    client_id = client_info.get("client_id")
    secret = client_info.get("client_secret")

    body = dict(data)
    body["client_id"] = client_id
    headers = {}

    if secret and method == "client_secret_post":
        body["client_secret"] = secret

    elif secret and method == "client_secret_basic":
        raw = f"{client_id}:{secret}".encode("utf-8")
        headers["Authorization"] = (
            "Basic " + base64.b64encode(raw).decode("ascii")
        )
        body.pop("client_secret", None)

    return headers, body


async def token_request(http, endpoints, client_info, data):
    """
    Single token-endpoint request with one auth method.
    """

    headers, body = build_client_auth(client_info, data)

    headers["Accept"] = "application/json"
    headers["Content-Type"] = (
        "application/x-www-form-urlencoded"
    )

    resp = await http.post(
        endpoints["token_endpoint"],
        data=body,
        headers=headers,
    )

    print(
        f"[Token] {endpoints['token_endpoint']} "
        f"-> HTTP {resp.status_code}"
    )

    if resp.status_code != 200:
        raise RuntimeError(
            f"Token endpoint error: HTTP {resp.status_code}: "
            f"{resp.text[:500]}"
        )

    tokens = resp.json()

    if "access_token" not in tokens:
        raise RuntimeError(
            "Token response missing access_token: "
            f"{resp.text[:500]}"
        )

    return tokens


async def register_client(http, endpoints, scopes):
    """
    Dynamic Client Registration. Tries client_secret_post
    first (single body-auth method), then public client.
    """

    variants = [
        {"token_endpoint_auth_method": "client_secret_post"},
        {"token_endpoint_auth_method": "none"},
        {},
    ]

    last_error = None

    for extra in variants:

        payload = {
            "client_name": "Porosh Linear MCP Client",
            "redirect_uris": [REDIRECT_URI],
            "grant_types": [
                "authorization_code",
                "refresh_token",
            ],
            "response_types": ["code"],
            "scope": scopes,
            **extra,
        }

        resp = await http.post(
            endpoints["registration_endpoint"],
            json=payload,
            headers={"Accept": "application/json"},
        )

        requested = extra.get(
            "token_endpoint_auth_method",
            "server default",
        )

        print(
            f"[Register] HTTP {resp.status_code} "
            f"(requested auth_method={requested})"
        )

        if resp.status_code in (200, 201):
            info = resp.json()
            print(f"[Register] client_id: {info.get('client_id')}")
            print(
                "[Register] auth method:",
                info.get("token_endpoint_auth_method"),
            )
            return info

        last_error = (
            f"HTTP {resp.status_code}: {resp.text[:300]}"
        )

    raise RuntimeError(
        f"Dynamic client registration failed. {last_error}"
    )


async def browser_authorization(
    endpoints,
    client_info,
    scopes,
    resource,
):
    """
    Open the browser, wait for the localhost callback,
    validate state, return (code, code_verifier).
    """

    verifier, challenge = make_pkce()
    state = secrets.token_urlsafe(24)

    params = {
        "response_type": "code",
        "client_id": client_info["client_id"],
        "redirect_uri": REDIRECT_URI,
        "scope": scopes,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }

    if resource:
        params["resource"] = resource

    auth_url = (
        f"{endpoints['authorization_endpoint']}?"
        f"{urlencode(params)}"
    )

    print()
    print("=" * 70)
    print("OPENING LINEAR AUTHORIZATION PAGE")
    print("=" * 70)
    print()
    print("If the browser does not open, copy this URL manually:")
    print()
    print(auth_url)
    print()

    server = OAuthCallbackServer()
    await server.start()

    try:
        try:
            webbrowser.open(auth_url)
        except Exception as exc:
            print(
                f"[Auth] Could not open browser ({exc}). "
                "Use the URL printed above."
            )

        print(
            "Waiting for approval in the browser "
            f"(timeout {AUTH_TIMEOUT_SECONDS}s)..."
        )

        callback_url = await asyncio.wait_for(
            server.wait_for_callback(),
            timeout=AUTH_TIMEOUT_SECONDS,
        )

    finally:
        await server.stop()

    parsed = urlparse(callback_url)
    callback_params = parse_qs(parsed.query)

    if "error" in callback_params:
        raise RuntimeError(
            f"OAuth error: {callback_params['error'][0]}"
        )

    if "code" not in callback_params:
        raise RuntimeError(
            "No authorization code in callback URL."
        )

    returned_state = callback_params.get("state", [None])[0]

    if returned_state != state:
        raise RuntimeError(
            "OAuth state mismatch — possible CSRF, aborting."
        )

    print("[Auth] Authorization code received and verified.")

    return callback_params["code"][0], verifier


async def full_oauth_dance(force_new_client: bool = False) -> dict:
    """
    Full flow: discover -> register -> browser -> token exchange.
    """

    state = load_state()

    if force_new_client:
        state.pop("client", None)
        state.pop("endpoints", None)
        state.pop("scopes", None)
        state.pop("resource", None)
        save_state(state)

    client_info = state.get("client")
    endpoints = state.get("endpoints")
    scopes = state.get("scopes")
    resource = state.get("resource")

    async with httpx2.AsyncClient(timeout=30.0) as http:

        if not (client_info and endpoints):
            disc = await discover_endpoints(http)

            endpoints = disc["endpoints"]
            scopes = disc["scopes"]
            resource = disc["resource"]

            client_info = await register_client(
                http, endpoints, scopes
            )

            state["client"] = client_info
            state["endpoints"] = endpoints
            state["scopes"] = scopes
            state["resource"] = resource
            save_state(state)

        else:
            print(
                "[Register] Reusing client registration "
                "from state file."
            )

    print()
    print("[Auth] Requesting authorization code via browser...")

    code, verifier = await browser_authorization(
        endpoints,
        client_info,
        scopes or FALLBACK_SCOPES,
        resource,
    )

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
    }

    if resource:
        data["resource"] = resource

    try:
        async with httpx2.AsyncClient(timeout=30.0) as http:
            tokens = await token_request(
                http, endpoints, client_info, data
            )

    except RuntimeError as exc:
        if (
            not force_new_client
            and "invalid_client" in str(exc).lower()
        ):
            print()
            print(
                "[Auth] Server rejected the client "
                "registration. Re-registering once..."
            )
            return await full_oauth_dance(
                force_new_client=True
            )
        raise

    expires_in = tokens.get("expires_in") or 3600
    tokens["expires_at"] = time.time() + int(expires_in) - 60

    state["tokens"] = tokens
    save_state(state)

    print()
    print("[Auth] SUCCESS — tokens obtained and cached.")

    return tokens


async def refresh_tokens(state: dict) -> dict:
    """
    Refresh the access token using the stored refresh token.
    """

    tokens = state["tokens"]

    endpoints = state.get("endpoints") or FALLBACK_ENDPOINTS
    client_info = state.get("client") or {}

    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
    }

    resource = state.get("resource")
    if resource:
        data["resource"] = resource

    async with httpx2.AsyncClient(timeout=30.0) as http:
        new_tokens = await token_request(
            http, endpoints, client_info, data
        )

    new_tokens.setdefault(
        "refresh_token",
        tokens.get("refresh_token"),
    )

    expires_in = new_tokens.get("expires_in") or 3600
    new_tokens["expires_at"] = (
        time.time() + int(expires_in) - 60
    )

    state["tokens"] = new_tokens
    save_state(state)

    print("[Auth] Token refreshed.")

    return new_tokens


# ============================================================
# MCP session helpers
# ============================================================

def is_auth_error(text: str) -> bool:
    lowered = str(text).lower()
    markers = (
        "401",
        "unauthorized",
        "invalid_token",
        "access token",
        "authentication",
        "authorization",
    )
    return any(marker in lowered for marker in markers)


async def safe_call_tool(client, name, arguments):
    """
    Call a tool, tolerating slightly different
    call_tool() signatures across SDK versions.
    """

    try:
        return await client.call_tool(
            name, arguments=arguments
        )
    except TypeError:
        return await client.call_tool(name, arguments)


def tool_requires_arguments(tool) -> bool:
    """
    True if the tool's input schema declares required
    parameters. Tools with required args (e.g. get_issue
    needing `id`) cannot be called with empty arguments.
    """

    schema = getattr(tool, "inputSchema", None) or {}

    try:
        return bool(schema.get("required"))
    except Exception:
        return False


def result_text(result) -> str:
    """
    Collect all text content from a tool result.
    """

    parts = []

    for content in getattr(result, "content", []) or []:
        text = getattr(content, "text", None)
        if text:
            parts.append(text)

    return "\n".join(parts)


def result_looks_like_error(result) -> bool:
    """
    Detect tool errors even when the SDK does not set
    isError (this fork returns validation errors as plain
    text results).
    """

    if getattr(result, "isError", False):
        return True

    joined = result_text(result).lower()

    error_markers = (
        "input validation error",
        "invalid arguments for tool",
        "expected string, received undefined",
        "unauthorized",
        "forbidden",
    )

    return any(marker in joined for marker in error_markers)


def print_issues_pretty(raw_text: str) -> bool:
    """
    If raw_text is a Linear list_issues JSON payload,
    print it in a clean human-readable format.

    Returns True if pretty-printing happened.
    """

    try:
        data = json.loads(raw_text)
    except Exception:
        return False

    if not (isinstance(data, dict) and "issues" in data):
        return False

    issues = data.get("issues", [])

    for issue in issues:
        print()
        print(
            f"{issue.get('id')}  "
            f"[{issue.get('status')}]  "
            f"{issue.get('title')}"
        )

        if issue.get("team"):
            print(f"   Team: {issue.get('team')}")

        if issue.get("url"):
            print(f"   {issue.get('url')}")

    print()
    print(f"Total: {len(issues)} issues")

    return True


# ============================================================
# MCP session
# ============================================================

async def run_session(access_token: str):
    """
    Connect to Linear MCP and run the demo.
    Returns (True, None) on success, (False, error) on failure.
    """

    try:
        async with httpx2.AsyncClient(
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=MCP_HTTP_TIMEOUT,
        ) as http_client:

            transport = streamable_http_client(
                MCP_SERVER_URL,
                http_client=http_client,
            )

            async with Client(transport) as client:

                print()
                print("=" * 70)
                print("CONNECTED TO LINEAR MCP SERVER")
                print("=" * 70)

                # ----------------------------------------
                # Discover tools
                # ----------------------------------------

                print()
                print("=" * 70)
                print("AVAILABLE LINEAR MCP TOOLS")
                print("=" * 70)

                tools_result = await client.list_tools()

                for index, tool in enumerate(
                    tools_result.tools,
                    start=1,
                ):
                    print()
                    print(f"{index}. {tool.name}")

                    if tool.description:
                        first_line = (
                            tool.description.split("\n")[0]
                        )
                        print(f"   {first_line}")

                print()
                print(f"Total tools: {len(tools_result.tools)}")

                # ----------------------------------------
                # Call Linear's list_issues tool
                #
                # Confirmed real tool name on Linear's MCP
                # server. Empty arguments are valid for it.
                # Fallbacks never include tools that REQUIRE
                # arguments (like get_issue, which needs id).
                # ----------------------------------------

                print()
                print("=" * 70)
                print("FETCHING LINEAR ISSUES")
                print("=" * 70)

                candidates = ["list_issues"]

                for tool in tools_result.tools:

                    name = tool.name

                    if name in candidates:
                        continue

                    lowered = name.lower()

                    matches_issues = (
                        "issue" in lowered
                        and any(
                            keyword in lowered
                            for keyword in (
                                "list",
                                "search",
                            )
                        )
                    )

                    # get_workspace needs no arguments and
                    # proves connectivity if issues fail.
                    matches_workspace = (
                        lowered == "get_workspace"
                    )

                    if (
                        (matches_issues or matches_workspace)
                        and not tool_requires_arguments(tool)
                    ):
                        candidates.append(name)

                called = False

                for candidate in candidates:

                    tool_exists = any(
                        tool.name == candidate
                        for tool in tools_result.tools
                    )

                    if not tool_exists:
                        print(
                            f"[Tools] '{candidate}' not on "
                            "server; skipping."
                        )
                        continue

                    print()
                    print(f"[Tools] Calling: {candidate}")

                    try:
                        result = await safe_call_tool(
                            client, candidate, {}
                        )
                    except Exception as call_exc:
                        print(
                            f"[Tools] {candidate} failed: "
                            f"{call_exc}"
                        )
                        continue

                    if result_looks_like_error(result):
                        print(
                            f"[Tools] {candidate} returned an "
                            "error; trying next candidate."
                        )
                        print(result_text(result)[:300])
                        continue

                    print()
                    print("=" * 70)
                    print(f"RESULT ({candidate})")
                    print("=" * 70)

                    raw_text = result_text(result)

                    if not print_issues_pretty(raw_text):
                        # Not an issues payload — print raw.
                        print(raw_text)

                    called = True
                    break

                if not called:
                    print()
                    print(
                        "[Warning] No suitable tool succeeded. "
                        "Pick one from the list above and call "
                        "it with client.call_tool(name, "
                        "arguments={...})."
                    )

        return True, None

    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


# ============================================================
# Main
# ============================================================

async def main():

    print()
    print("=" * 70)
    print("LINEAR MCP CLIENT (manual OAuth 2.1 + PKCE)")
    print("=" * 70)

    state = load_state()
    tokens = state.get("tokens")

    # --------------------------------------------------------
    # Fast path: cached token (no browser needed).
    # --------------------------------------------------------

    if tokens and tokens.get("access_token"):

        expires_at = tokens.get("expires_at")

        if (
            expires_at
            and time.time() >= float(expires_at)
            and tokens.get("refresh_token")
        ):
            print(
                "[Auth] Cached access token expired — "
                "refreshing first."
            )
            try:
                tokens = await refresh_tokens(state)
            except Exception as exc:
                print(
                    f"[Auth] Refresh failed ({exc}); "
                    "will try the old token anyway."
                )

        print(
            "[Auth] Connecting with cached token "
            "(no browser needed)."
        )

        ok, err = await run_session(tokens["access_token"])

        if ok:
            return

        print(f"[Session] Failed: {err}")

        if is_auth_error(err):

            if tokens.get("refresh_token"):
                print("[Auth] Trying refresh...")

                try:
                    tokens = await refresh_tokens(state)

                    ok, err = await run_session(
                        tokens["access_token"]
                    )

                    if ok:
                        return

                    print(f"[Session] Still failing: {err}")

                except Exception as exc:
                    print(f"[Auth] Refresh failed: {exc}")

        else:
            print(
                "[Session] Error does not look auth-related; "
                "not re-authorizing."
            )
            return

    # --------------------------------------------------------
    # Slow path: full OAuth flow (browser opens once).
    # --------------------------------------------------------

    print()
    print(
        "[Auth] Starting full OAuth flow — "
        "browser will open."
    )

    tokens = await full_oauth_dance()

    ok, err = await run_session(tokens["access_token"])

    if not ok:
        raise RuntimeError(
            f"MCP session failed after fresh login: {err}"
        )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print()
        print("Program interrupted by user.")

    except BaseException as exc:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print()

        # TaskGroup errors arrive wrapped in ExceptionGroup.
        # Unwrap them so nothing is hidden.

        if isinstance(exc, BaseExceptionGroup):

            for index, sub_exc in enumerate(
                exc.exceptions,
                start=1,
            ):
                print(f"--- Sub-exception {index} ---")

                traceback.print_exception(
                    type(sub_exc),
                    sub_exc,
                    sub_exc.__traceback__,
                )

        else:

            traceback.print_exception(
                type(exc),
                exc,
                exc.__traceback__,
            )

        if is_auth_error(str(exc)):
            print()
            print(
                "Tip: auth-related failure. Reset cached "
                "credentials and retry:"
            )
            print(f"    rm {STATE_FILE}")
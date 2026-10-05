import asyncio
import webbrowser
from urllib.parse import parse_qs, urlparse

import httpx2
from pydantic import AnyUrl
from mcp import Client

from mcp.client.auth import (
    AuthorizationCodeResult,
    OAuthClientProvider,
    TokenStorage,
)

from mcp.client.streamable_http import streamable_http_client

from mcp.shared.auth import (
    OAuthClientInformationFull,
    OAuthClientMetadata,
    OAuthToken,
)


# ============================================================
# Configuration
# ============================================================

MCP_SERVER_URL = "https://mcp.trello.com/v1"

REDIRECT_URI = "http://localhost:3030/callback"

CALLBACK_HOST = "127.0.0.1"
CALLBACK_PORT = 3030


# ============================================================
# Token Storage
# ============================================================

class InMemoryTokenStorage(TokenStorage):

    def __init__(self):
        self.tokens = None
        self.client_info = None

    async def get_tokens(self):
        return self.tokens

    async def set_tokens(self, tokens: OAuthToken):
        self.tokens = tokens

    async def get_client_info(self):
        return self.client_info

    async def set_client_info(
        self,
        client_info: OAuthClientInformationFull
    ):
        self.client_info = client_info


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

            # Give the URL to callback_handler().
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
                    <title>Trello OAuth</title>
                </head>
                <body>
                    <h2>Authorization successful!</h2>
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
# OAuth Callback Server Instance
# ============================================================

callback_server = OAuthCallbackServer()


# ============================================================
# Open Browser
# ============================================================

async def redirect_handler(
    authorization_url: str,
):

    print()
    print("=" * 70)
    print("OPENING TRELLO AUTHORIZATION PAGE")
    print("=" * 70)

    print()
    print("Browser authorization URL generated.")
    print()
    print("Opening browser...")
    print()

    # Automatically open browser.
    webbrowser.open(authorization_url)


# ============================================================
# OAuth Callback
# ============================================================

async def callback_handler() -> AuthorizationCodeResult:

    print()
    print("=" * 70)
    print("WAITING FOR TRELLO OAUTH CALLBACK")
    print("=" * 70)

    print()
    print(
        "Approve Trello access in your browser."
    )

    print(
        "After approval, the browser will automatically "
        "return to localhost."
    )

    print()
    print(
        "No callback URL copy/paste is required."
    )

    # Wait for local HTTP server to receive callback.
    callback_url = await callback_server.wait_for_callback()

    print()
    print("[OAuth] Processing callback...")

    parsed = urlparse(callback_url)

    params = parse_qs(parsed.query)

    if "error" in params:

        raise RuntimeError(
            f"OAuth error: {params['error'][0]}"
        )

    if "code" not in params:

        raise RuntimeError(
            "Authorization code was not found "
            "in callback URL."
        )

    print("[OAuth] Authorization code parsed successfully.")

    return AuthorizationCodeResult(
        code=params["code"][0],

        state=params.get(
            "state",
            [None],
        )[0],

        iss=params.get(
            "iss",
            [None],
        )[0],
    )


# ============================================================
# Main
# ============================================================

async def main():

    print()
    print("Starting Trello MCP Client...")
    print()

    # --------------------------------------------------------
    # Start localhost OAuth callback server FIRST.
    # --------------------------------------------------------

    await callback_server.start()

    try:

        # ----------------------------------------------------
        # OAuth Provider
        # ----------------------------------------------------

        oauth = OAuthClientProvider(

            server_url=MCP_SERVER_URL,

            client_metadata=OAuthClientMetadata(

                client_name="Tiemoon Trello MCP Client",

                redirect_uris=[
                    AnyUrl(REDIRECT_URI)
                ],

                grant_types=[
                    "authorization_code",
                    "refresh_token",
                ],

                response_types=[
                    "code"
                ],
            ),

            storage=InMemoryTokenStorage(),

            redirect_handler=redirect_handler,

            callback_handler=callback_handler,
        )

        # ----------------------------------------------------
        # HTTP Client
        # ----------------------------------------------------

        async with httpx2.AsyncClient(
            auth=oauth
        ) as http_client:

            # ------------------------------------------------
            # MCP Streamable HTTP transport
            # ------------------------------------------------

            transport = streamable_http_client(
                MCP_SERVER_URL,
                http_client=http_client,
            )

            # ------------------------------------------------
            # MCP Client
            # ------------------------------------------------

            async with Client(transport) as client:

                # ============================================
                # Initialize MCP session
                # ============================================

                print()
                print("=" * 70)
                print("CONNECTED TO TRELLO MCP SERVER")
                print("=" * 70)
                print()

                # ============================================
                # Discover tools
                # ============================================

                print("=" * 70)
                print("AVAILABLE MCP TOOLS")
                print("=" * 70)

                result = await client.list_tools()

                for index, tool in enumerate(
                    result.tools,
                    start=1,
                ):

                    print()
                    print(
                        f"{index}. {tool.name}"
                    )

                    if tool.description:

                        print(
                            f"   {tool.description}"
                        )

                print()
                print(
                    f"Total tools: {len(result.tools)}"
                )

                # ============================================
                # Call Trello MCP Tool
                # ============================================

                print()
                print("=" * 70)
                print("CALLING trelloSearch")
                print("=" * 70)

                result = await client.call_tool(
                    "trelloSearch",
                    arguments={
                        "action": "search_cards",
                        "query": "ticket",
                    },
                )

                print()
                print("=" * 70)
                print("RESULT")
                print("=" * 70)

                for content in result.content:

                    if hasattr(content, "text"):

                        print(content.text)

    finally:

        # ----------------------------------------------------
        # Always stop local callback server.
        # ----------------------------------------------------

        await callback_server.stop()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print()
        print("Program interrupted by user.")

    except Exception as exc:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print()
        print(type(exc).__name__)
        print(exc)

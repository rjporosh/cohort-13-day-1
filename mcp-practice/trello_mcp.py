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
# Open Browser
# ============================================================

async def redirect_handler(authorization_url: str):

    print()
    print("=" * 70)
    print("OPENING TRELLO AUTHORIZATION PAGE")
    print("=" * 70)

    print(authorization_url)

    # Automatically open browser
    webbrowser.open(authorization_url)


# ============================================================
# OAuth Callback
# ============================================================

async def callback_handler() -> AuthorizationCodeResult:

    print()
    print("=" * 70)
    print("TRELLO AUTHORIZATION")
    print("=" * 70)

    print()
    print(
        "After approving Trello access, "
        "copy the URL from your browser."
    )

    print()

    callback_url = input(
        "Paste callback URL here: "
    ).strip()

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

    return AuthorizationCodeResult(
        code=params["code"][0],

        state=params.get(
            "state",
            [None]
        )[0],

        iss=params.get(
            "iss",
            [None]
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
    # OAuth Provider
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # HTTP Client
    # --------------------------------------------------------
    async with httpx2.AsyncClient(
        auth=oauth
    ) as http_client:

        # ----------------------------------------------------
        # MCP Streamable HTTP transport
        # ----------------------------------------------------
        transport = streamable_http_client(
            MCP_SERVER_URL,
            http_client=http_client
        )

        # ----------------------------------------------------
        # MCP Client
        # ----------------------------------------------------

        async with Client(transport) as client:

            # =================================================
            # Initialize MCP session
            # =================================================

            print()
            print("Connected to Trello MCP Server!")
            print()
            print()

            # =================================================
            # Discover tools
            # =================================================

            print("=" * 70)
            print("AVAILABLE MCP TOOLS")
            print("=" * 70)

            result = await client.list_tools()

            for index, tool in enumerate(
                result.tools,
                start=1
            ):

                print()
                print(f"{index}. {tool.name}")

                if tool.description:

                    print(
                        f"   {tool.description}"
                    )

            print()
            print(
                f"Total tools: {len(result.tools)}"
            )

        # ============================================================
        # Call Trello MCP Tool
        # ============================================================

            print()
            print("=" * 70)
            print("CALLING trelloSearch")
            print("=" * 70)

            result = await client.call_tool(
                "trelloSearch",
                arguments={
                    "action": "search_cards",
                    "query": "ticket"
                }
            )

            print()
            print("RESULT")
            print("=" * 70)

            for content in result.content:

                if hasattr(content, "text"):
                    print(content.text)            

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
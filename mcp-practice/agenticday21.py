import asyncio
import json
import webbrowser

from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx2

from pydantic import AnyUrl

from openai import OpenAI

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

MODEL = "gpt-5.6"


# ============================================================
# OpenAI Client
# ============================================================

openai_client = OpenAI()


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
    print("Waiting for Trello authorization...")
    print()
    print("No copy/paste is required.")
    print("The browser callback will be captured automatically.")
    print()

    callback_data = {}

    class CallbackHandler(BaseHTTPRequestHandler):

        def do_GET(self):

            parsed = urlparse(self.path)

            if parsed.path != "/callback":

                self.send_response(404)
                self.end_headers()

                return

            params = parse_qs(parsed.query)

            callback_data.update(params)

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                b"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Trello Authorization</title>
</head>
<body>
    <h2>Trello authorization successful.</h2>
    <p>You can close this browser tab and return to the terminal.</p>
</body>
</html>
"""
            )

        def log_message(self, format, *args):
            # Disable default HTTP server logs
            pass

    # --------------------------------------------------------
    # Start localhost callback server
    # --------------------------------------------------------

    server = HTTPServer(
        ("127.0.0.1", 3030),
        CallbackHandler
    )

    print("Callback server started:")
    print("http://localhost:3030/callback")
    print()

    # --------------------------------------------------------
    # Wait for exactly one browser callback
    # --------------------------------------------------------

    await asyncio.to_thread(
        server.handle_request
    )

    server.server_close()

    # --------------------------------------------------------
    # Check OAuth error
    # --------------------------------------------------------

    if "error" in callback_data:

        raise RuntimeError(
            f"OAuth error: {callback_data['error'][0]}"
        )

    # --------------------------------------------------------
    # Check authorization code
    # --------------------------------------------------------

    if "code" not in callback_data:

        raise RuntimeError(
            "Authorization code was not found "
            "in callback request."
        )

    print()
    print("=" * 70)
    print("TRELLO OAUTH CALLBACK RECEIVED")
    print("=" * 70)

    print()
    print("Authorization code received automatically.")
    print()

    # --------------------------------------------------------
    # Return OAuth result
    # --------------------------------------------------------

    return AuthorizationCodeResult(

        code=callback_data["code"][0],

        state=callback_data.get(
            "state",
            [None]
        )[0],

        iss=callback_data.get(
            "iss",
            [None]
        )[0],
    )


# ============================================================
# Convert MCP Tools → OpenAI Tools
# ============================================================

def convert_mcp_tools_to_openai_tools(mcp_tools):

    openai_tools = []

    for tool in mcp_tools:

        openai_tool = {
            "type": "function",
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        }

        openai_tools.append(openai_tool)

    return openai_tools


# ============================================================
# Agent
# ============================================================

async def run_agent(client, mcp_tools):

    # --------------------------------------------------------
    # Convert MCP tool definitions to LLM tool definitions
    # --------------------------------------------------------

    tools = convert_mcp_tools_to_openai_tools(
        mcp_tools
    )

    print()
    print("=" * 70)
    print("AGENT")
    print("=" * 70)

    print()
    print("Available MCP tools:")
    print()

    for tool in mcp_tools:

        print(f"- {tool.name}")

    print()

    # --------------------------------------------------------
    # User request
    # --------------------------------------------------------

    user_request = input(
        "What would you like me to do in Trello?\n> "
    ).strip()

    if not user_request:

        return

    # --------------------------------------------------------
    # Initial conversation
    # --------------------------------------------------------

    conversation = [
        {
            "role": "user",
            "content": user_request
        }
    ]

    # --------------------------------------------------------
    # Agent loop
    # --------------------------------------------------------

    while True:

        print()
        print("-" * 70)
        print("ASKING LLM...")
        print("-" * 70)

        response = openai_client.responses.create(

            model=MODEL,

            instructions="""
You are a Trello assistant.

You have access to Trello capabilities through MCP tools.

Analyze the user's request and select the appropriate MCP
tool when necessary.

Do not assume a tool name.

Use the tool descriptions and input schemas to determine
which MCP tool should be called.

IMPORTANT PAGINATION RULES:

- Skip the cursor parameter on the first call to a tool.

If a tool requires an ID or other information that is not
available, use another appropriate MCP tool first to obtain
that information.

After receiving tool results, continue reasoning and call
additional tools if necessary.

When the task is complete, provide a concise natural-language
answer to the user.
""",

            tools=tools,

            input=conversation,
        )

        # ----------------------------------------------------
        # Add LLM response to conversation
        # ----------------------------------------------------

        conversation += response.output

        # ----------------------------------------------------
        # Check whether the LLM requested a tool
        # ----------------------------------------------------

        tool_calls = [

            item

            for item in response.output

            if item.type == "function_call"
        ]

        # ----------------------------------------------------
        # No tool call → final answer
        # ----------------------------------------------------

        if not tool_calls:

            print()
            print("=" * 70)
            print("FINAL ANSWER")
            print("=" * 70)

            print()

            print(
                response.output_text
            )

            break

        # ----------------------------------------------------
        # Execute MCP tool calls
        # ----------------------------------------------------

        for tool_call in tool_calls:

            tool_name = tool_call.name

            arguments = json.loads(
                tool_call.arguments
            )

            print()
            print("=" * 70)
            print("LLM SELECTED MCP TOOL")
            print("=" * 70)

            print()
            print("Tool:")
            print(tool_name)

            print()
            print("Arguments:")

            print(
                json.dumps(
                    arguments,
                    indent=2
                )
            )

            # ------------------------------------------------
            # Call MCP tool
            # ------------------------------------------------

            result = await client.call_tool(

                tool_name,

                arguments=arguments
            )

            # ------------------------------------------------
            # Extract MCP result
            # ------------------------------------------------

            result_parts = []

            for content in result.content:

                if hasattr(content, "text"):

                    result_parts.append(
                        content.text
                    )

                else:

                    result_parts.append(
                        str(content)
                    )

            tool_result = "\n".join(
                result_parts
            )

            print()
            print("=" * 70)
            print("MCP TOOL RESULT")
            print("=" * 70)

            print()

            print(tool_result)

            # ------------------------------------------------
            # Send MCP result back to LLM
            # ------------------------------------------------

            conversation.append(

                {
                    "type": "function_call_output",

                    "call_id": tool_call.call_id,

                    "output": tool_result,
                }
            )


# ============================================================
# Main
# ============================================================

async def main():

    print()
    print("Starting Trello MCP Agent...")
    print()

    # ========================================================
    # OAuth Provider
    # ========================================================

    oauth = OAuthClientProvider(

        server_url=MCP_SERVER_URL,

        client_metadata=OAuthClientMetadata(

            client_name="Tiemoon Trello MCP Agent",

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

    # ========================================================
    # HTTP Client
    # ========================================================

    async with httpx2.AsyncClient(
        auth=oauth
    ) as http_client:

        # ====================================================
        # MCP Transport
        # ====================================================

        transport = streamable_http_client(

            MCP_SERVER_URL,

            http_client=http_client
        )

        # ====================================================
        # MCP Client
        # ====================================================

        async with Client(transport) as client:

            print()
            print(
                "Connected to Trello MCP Server!"
            )

            # =================================================
            # Discover MCP tools
            # =================================================

            result = await client.list_tools()

            print()
            print("=" * 70)
            print("MCP TOOL DISCOVERY")
            print("=" * 70)

            print()

            print(
                f"Discovered {len(result.tools)} tools."
            )

            # =================================================
            # Run Agent
            # =================================================

            await run_agent(

                client,

                result.tools
            )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())

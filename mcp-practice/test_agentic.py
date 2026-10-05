import asyncio
import json
import webbrowser

from urllib.parse import parse_qs, urlparse

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

CALLBACK_HOST = "127.0.0.1"
CALLBACK_PORT = 3030

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

    async def set_tokens(
        self,
        tokens: OAuthToken,
    ):
        self.tokens = tokens

    async def get_client_info(self):
        return self.client_info

    async def set_client_info(
        self,
        client_info: OAuthClientInformationFull,
    ):
        self.client_info = client_info


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
    print(authorization_url)
    print()

    try:
        webbrowser.open(
            authorization_url
        )

        print(
            "Browser opened automatically."
        )

    except Exception as exc:

        print(
            "Could not open browser automatically."
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        print()
        print(
            "Please open the authorization URL manually."
        )


# ============================================================
# OAuth Callback - AUTO
# ============================================================

async def callback_handler() -> AuthorizationCodeResult:

    print()
    print("=" * 70)
    print("TRELLO OAUTH CALLBACK")
    print("=" * 70)

    print()
    print(
        f"Waiting for callback on {REDIRECT_URI}"
    )

    print()
    print(
        "Approve Trello access in the browser."
    )

    # --------------------------------------------------------
    # Future used to receive OAuth callback result
    # --------------------------------------------------------

    loop = asyncio.get_running_loop()

    callback_future = loop.create_future()

    # --------------------------------------------------------
    # Callback HTTP handler
    # --------------------------------------------------------

    async def handle_callback_request(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):

        try:

            # ------------------------------------------------
            # Read browser HTTP request
            # ------------------------------------------------

            request_data = await asyncio.wait_for(
                reader.read(8192),
                timeout=30,
            )

            request_text = request_data.decode(
                "utf-8",
                errors="replace",
            )

            # ------------------------------------------------
            # Get first HTTP request line
            # ------------------------------------------------

            request_line = request_text.split(
                "\r\n",
                1,
            )[0]

            request_parts = request_line.split()

            if len(request_parts) < 2:
                raise RuntimeError(
                    "Invalid OAuth callback request."
                )

            request_target = request_parts[1]

            # ------------------------------------------------
            # Parse callback URL
            # ------------------------------------------------

            parsed = urlparse(
                request_target
            )

            params = parse_qs(
                parsed.query
            )

            # ------------------------------------------------
            # OAuth error
            # ------------------------------------------------

            if "error" in params:

                error = params.get(
                    "error",
                    ["unknown"],
                )[0]

                description = params.get(
                    "error_description",
                    ["No description"],
                )[0]

                raise RuntimeError(
                    f"OAuth error: "
                    f"{error} - {description}"
                )

            # ------------------------------------------------
            # Authorization code
            # ------------------------------------------------

            if "code" not in params:

                raise RuntimeError(
                    "Authorization code was not found "
                    "in OAuth callback."
                )

            code = params["code"][0]

            state = params.get(
                "state",
                [None],
            )[0]

            iss = params.get(
                "iss",
                [None],
            )[0]

            # ------------------------------------------------
            # Browser success page
            # ------------------------------------------------

            response_body = """
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
""".strip()

            response_bytes = response_body.encode(
                "utf-8"
            )

            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(response_bytes)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode(
                "utf-8"
            ) + response_bytes

            writer.write(
                http_response
            )

            await writer.drain()

            # ------------------------------------------------
            # Return OAuth result
            # ------------------------------------------------

            if not callback_future.done():

                callback_future.set_result(

                    AuthorizationCodeResult(
                        code=code,
                        state=state,
                        iss=iss,
                    )
                )

        except Exception as exc:

            # ------------------------------------------------
            # Browser error page
            # ------------------------------------------------

            error_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Trello Authorization Error</title>
</head>
<body>
    <h2>Trello authorization failed.</h2>
    <p>{str(exc)}</p>
    <p>You can close this browser tab.</p>
</body>
</html>
""".strip()

            error_bytes = error_body.encode(
                "utf-8"
            )

            try:

                http_response = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    f"Content-Length: {len(error_bytes)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode(
                    "utf-8"
                ) + error_bytes

                writer.write(
                    http_response
                )

                await writer.drain()

            except Exception:
                pass

            if not callback_future.done():

                callback_future.set_exception(
                    exc
                )

        finally:

            try:

                writer.close()

                await writer.wait_closed()

            except Exception:
                pass

    # --------------------------------------------------------
    # Start local callback server
    # --------------------------------------------------------

    server = await asyncio.start_server(
        handle_callback_request,
        CALLBACK_HOST,
        CALLBACK_PORT,
    )

    try:

        print()
        print(
            "OAuth callback server started."
        )

        print(
            "Waiting for Trello authorization..."
        )

        print()

        # ----------------------------------------------------
        # Wait until browser redirects here
        # ----------------------------------------------------

        result = await callback_future

        print()
        print(
            "OAuth callback received successfully."
        )

        return result

    finally:

        # ----------------------------------------------------
        # Stop callback server
        # ----------------------------------------------------

        server.close()

        await server.wait_closed()

        print(
            "OAuth callback server stopped."
        )


# ============================================================
# Convert MCP Tools → OpenAI Tools
# ============================================================

def convert_mcp_tools_to_openai_tools(
    mcp_tools,
):

    openai_tools = []

    for tool in mcp_tools:

        openai_tool = {
            "type": "function",
            "name": tool.name,
            "description": (
                tool.description or ""
            ),
            "parameters": tool.input_schema,
        }

        openai_tools.append(
            openai_tool
        )

    return openai_tools


# ============================================================
# Agent
# ============================================================

async def run_agent(
    client,
    mcp_tools,
):

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

        print(
            f"- {tool.name}"
        )

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
            "content": user_request,
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

            print(
                tool_name
            )

            print()
            print("Arguments:")

            print(
                json.dumps(
                    arguments,
                    indent=2,
                )
            )

            # ------------------------------------------------
            # Call MCP tool
            # ------------------------------------------------

            result = await client.call_tool(
                tool_name,
                arguments=arguments,
            )

            # ------------------------------------------------
            # Extract MCP result
            # ------------------------------------------------

            result_parts = []

            for content in result.content:

                if hasattr(
                    content,
                    "text",
                ):

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

            print(
                tool_result
            )

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
    print(
        "Starting Trello MCP Agent..."
    )
    print()

    # ========================================================
    # OAuth Provider
    # ========================================================

    oauth = OAuthClientProvider(

        server_url=MCP_SERVER_URL,

        client_metadata=OAuthClientMetadata(

            client_name="Porosh Trello MCP Agent",

            redirect_uris=[
                AnyUrl(
                    REDIRECT_URI
                )
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
            http_client=http_client,
        )

        # ====================================================
        # MCP Client
        # ====================================================

        async with Client(
            transport
        ) as client:

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
                result.tools,
            )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
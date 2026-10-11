
import asyncio
import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from mcp import Client


# ============================================================
# Configuration
# ============================================================

load_dotenv()

MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"
MODEL = "gpt-5.6"
MAX_AGENT_STEPS = 10

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Please check your .env file."
    )

openai_client = OpenAI(api_key=api_key)


# ============================================================
# Convert MCP tools into OpenAI function tools
# ============================================================

def convert_mcp_tools_to_openai_tools(mcp_tools):
    """
    Convert tools discovered from the MCP server into the
    function-tool format required by the OpenAI Responses API.
    """

    openai_tools = []

    for tool in mcp_tools:
        openai_tools.append(
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
                "strict": False,
            }
        )

    return openai_tools


# ============================================================
# Extract MCP tool results
# ============================================================

def extract_tool_result(result):
    """
    Convert an MCP tool result into text that can be passed
    back to the LLM.
    """

    parts = []

    for content in result.content:
        if hasattr(content, "text"):
            parts.append(content.text)
        else:
            parts.append(str(content))

    text_result = "\n".join(parts)

    is_error = getattr(
        result,
        "isError",
        getattr(result, "is_error", False),
    )

    if is_error:
        return f"MCP tool returned an error:\n{text_result}"

    if text_result:
        return text_result

    # Some tools may return structured content.
    structured_content = getattr(
        result,
        "structuredContent",
        getattr(result, "structured_content", None),
    )

    if structured_content is not None:
        return json.dumps(
            structured_content,
            ensure_ascii=False,
            default=str,
        )

    return json.dumps(
        {"message": "Tool returned no content."},
        ensure_ascii=False,
    )


# ============================================================
# Agent instructions
# ============================================================

AGENT_INSTRUCTIONS = """
You are an AI assistant for a task management application.

You have access to tools provided by an MCP server.

Your responsibilities:

1. Understand the user's request.
2. Select the most appropriate available tool.
3. Provide arguments that match the tool's input schema.
4. Use the actual task IDs returned by the server.
5. Never invent task IDs or claim a task operation succeeded
   unless the tool result confirms it.
6. For requests involving existing tasks, retrieve the relevant
   task information when necessary.
7. If a required argument is missing or ambiguous, ask the user
   for clarification instead of guessing.
8. Use the tool results to answer the user accurately.
9. If a tool returns an error, explain the error clearly.
10. Do not claim that an operation succeeded when it failed.

Available task management operations may include:
- Creating a task
- Retrieving a task by ID
- Listing all tasks
- Updating a task
- Deleting a task

Use the available tools dynamically. Do not assume that a
particular tool must be called for every request.

For destructive operations such as deleting a task, ask for
confirmation before executing unless the user has already
clearly confirmed the specific deletion.
"""


# ============================================================
# Process one user request
# ============================================================

async def process_user_request(
    client,
    openai_tools,
    user_request,
):
    """
    Run the agent loop:

    User request
        -> LLM selects a tool
        -> MCP tool executes
        -> Result returns to LLM
        -> LLM produces the final answer
    """

    conversation = [
        {
            "role": "user",
            "content": user_request,
        }
    ]

    for step in range(MAX_AGENT_STEPS):

        print(f"\n--- Agent step {step + 1} ---")
        print("Asking the LLM...")

        response = openai_client.responses.create(
            model=MODEL,
            instructions=AGENT_INSTRUCTIONS,
            tools=openai_tools,
            input=conversation,
        )

        # Preserve the model's output for the next iteration.
        conversation.extend(response.output)

        # Find function calls requested by the LLM.
        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # No tool calls means the model has produced its answer.
        if not tool_calls:
            return response.output_text

        # Execute each tool selected by the LLM.
        for tool_call in tool_calls:

            tool_name = tool_call.name

            print(f"\nSelected MCP tool: {tool_name}")

            try:
                arguments = json.loads(tool_call.arguments)

                if not isinstance(arguments, dict):
                    raise ValueError(
                        "Tool arguments must be a JSON object."
                    )

                print("Arguments:")
                print(
                    json.dumps(
                        arguments,
                        indent=2,
                        ensure_ascii=False,
                    )
                )

                # Generic invocation:
                # No hard-coded mapping for individual tools.
                result = await client.call_tool(
                    tool_name,
                    arguments=arguments,
                )

                tool_result = extract_tool_result(result)

            except Exception as exc:
                tool_result = (
                    f"Tool execution failed: "
                    f"{type(exc).__name__}: {exc}"
                )

            print("\nTool result:")
            print(tool_result)

            # Return the result to the LLM.
            conversation.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": tool_result,
                }
            )

    return (
        "The agent reached its maximum number of steps. "
        "Please try a simpler request."
    )


# ============================================================
# Main application
# ============================================================

async def main():

    print("Connecting to Task Management MCP Server...")
    print(MCP_SERVER_URL)

    # Client accepts the URL directly.
    # This avoids passing the transport tuple incorrectly.
    async with Client(MCP_SERVER_URL) as client:

        print("\nConnected to MCP server.")

        # Discover tools from the running MCP server.
        tool_result = await client.list_tools()
        mcp_tools = tool_result.tools

        print(f"\nDiscovered {len(mcp_tools)} MCP tools:")

        for tool in mcp_tools:
            print(f"  - {tool.name}")

        # Convert the discovered tools for the LLM.
        openai_tools = convert_mcp_tools_to_openai_tools(
            mcp_tools
        )

        print("\nTask Management AI Agent is ready.")
        print("Enter 'exit' to stop.\n")

        # Interactive conversation loop.
        while True:

            user_request = input("You: ").strip()

            if user_request.lower() in {
                "exit",
                "quit",
                "bye",
            }:
                print("Agent stopped.")
                break

            if not user_request:
                continue

            try:
                answer = await process_user_request(
                    client,
                    openai_tools,
                    user_request,
                )

                print(f"\nAgent: {answer}\n")

            except Exception as exc:
                print(
                    f"\nAgent error: "
                    f"{type(exc).__name__}: {exc}\n"
                )

# ============================================================
# Application entry point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())

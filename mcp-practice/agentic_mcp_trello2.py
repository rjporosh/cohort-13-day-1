import asyncio
import json
import os
import re
import threading
import webbrowser
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx2
from openai import OpenAI
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
# CONFIGURATION
# ============================================================

MCP_SERVER_URL = "https://mcp.trello.com/v1"

REDIRECT_URI = "http://localhost:3030/callback"

MODEL = "gpt-5.6"

MAX_AGENT_TURNS = 5

OPENAI_CLIENT = OpenAI()


# ============================================================
# AUTOMATIC OAUTH CALLBACK SERVER
# ============================================================

CALLBACK_HOST = "127.0.0.1"
CALLBACK_PORT = 3030

_callback_event = threading.Event()
_callback_url: str | None = None
_callback_server: HTTPServer | None = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """
    Handles the browser redirect from Trello.

    Example:

        http://localhost:3030/callback?code=...&state=...
    """

    def do_GET(self):
        global _callback_url

        parsed = urlparse(self.path)

        if parsed.path != "/callback":
            self.send_response(404)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8",
            )
            self.end_headers()

            self.wfile.write(
                b"<html><body><h2>Not Found</h2></body></html>"
            )
            return

        # Reconstruct complete callback URL
        _callback_url = (
            f"http://localhost:{CALLBACK_PORT}"
            f"{self.path}"
        )

        # Notify waiting callback handler
        _callback_event.set()

        # Browser response
        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8",
        )

        self.send_header(
            "Cache-Control",
            "no-store",
        )

        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Trello Authorization Complete</title>
        </head>
        <body
            style="
                font-family: Arial, sans-serif;
                text-align: center;
                padding-top: 80px;
            "
        >
            <h1>Authorization successful</h1>
            <p>You can close this browser tab.</p>
        </body>
        </html>
        """

        self.wfile.write(
            html.encode("utf-8")
        )

    def log_message(
        self,
        format,
        *args,
    ):
        # Silence default HTTP server logging.
        return


def start_callback_server() -> None:
    """
    Start the local OAuth callback server.

    The server listens on:

        http://127.0.0.1:3030/callback
    """

    global _callback_server
    global _callback_url

    # Reset previous callback state
    _callback_event.clear()
    _callback_url = None

    if _callback_server is not None:
        return

    try:
        _callback_server = HTTPServer(
            (
                CALLBACK_HOST,
                CALLBACK_PORT,
            ),
            OAuthCallbackHandler,
        )
    except OSError as exc:
        raise RuntimeError(
            f"Could not start OAuth callback server "
            f"on port {CALLBACK_PORT}. "
            f"Make sure port {CALLBACK_PORT} is free."
        ) from exc

    thread = threading.Thread(
        target=_callback_server.serve_forever,
        daemon=True,
    )

    thread.start()

    print()
    print(
        f"OAuth callback server started:"
    )
    print(
        f"http://localhost:{CALLBACK_PORT}/callback"
    )
    print()


def stop_callback_server() -> None:
    """
    Stop the local OAuth callback server.
    """

    global _callback_server

    if _callback_server is not None:
        try:
            _callback_server.shutdown()
        except Exception:
            pass

        try:
            _callback_server.server_close()
        except Exception:
            pass

        _callback_server = None


# ============================================================
# STATE
# ============================================================

@dataclass
class AgentState:
    """
    State maintained during the whole conversation.

    This is application state.
    It is separate from the LLM itself.
    """

    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    conversation: list[Any] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Trello context
    # --------------------------------------------------------

    workspace_id: str | None = None
    workspace_name: str | None = None

    board_id: str | None = None
    board_name: str | None = None

    list_id: str | None = None
    list_name: str | None = None

    card_id: str | None = None
    card_name: str | None = None

    # --------------------------------------------------------
    # General memory/context
    # --------------------------------------------------------

    values: dict[str, Any] = field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # Failed calls
    # --------------------------------------------------------

    failed_calls: set[str] = field(
        default_factory=set
    )

    # --------------------------------------------------------
    # Turn counter
    # --------------------------------------------------------

    total_turns: int = 0


# ============================================================
# STATE HELPERS
# ============================================================

def state_summary(
    state: AgentState,
) -> str:
    """
    Create a compact representation of the current state
    that can be supplied to the LLM.
    """

    state_data = {
        "workspace_id": state.workspace_id,
        "workspace_name": state.workspace_name,
        "board_id": state.board_id,
        "board_name": state.board_name,
        "list_id": state.list_id,
        "list_name": state.list_name,
        "card_id": state.card_id,
        "card_name": state.card_name,
        "values": state.values,
    }

    return json.dumps(
        state_data,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


def update_state_from_result(
    state: AgentState,
    result_text: str,
) -> None:
    """
    Try to extract useful Trello IDs/names from MCP results.

    This is intentionally generic.
    We do not hard-code a particular MCP tool.
    """

    try:
        data = json.loads(result_text)
    except Exception:
        return

    if not isinstance(
        data,
        (dict, list),
    ):
        return

    # --------------------------------------------------------
    # Recursively inspect MCP result
    # --------------------------------------------------------

    def visit(
        value: Any,
    ) -> None:

        if isinstance(value, dict):

            # ----------------------------------------------
            # Workspace
            # ----------------------------------------------

            if (
                "id" in value
                and isinstance(
                    value["id"],
                    str,
                )
            ):

                object_id = value["id"]

                name = value.get(
                    "name"
                )

                display_name = value.get(
                    "displayName"
                )

                # Workspace ARI
                if object_id.startswith(
                    "ari:cloud:trello::workspace/"
                ):

                    state.workspace_id = object_id

                    if isinstance(
                        name,
                        str,
                    ):
                        state.workspace_name = name

                    elif isinstance(
                        display_name,
                        str,
                    ):
                        state.workspace_name = (
                            display_name
                        )

                # Board ARI
                elif object_id.startswith(
                    "ari:cloud:trello::board/"
                ):

                    state.board_id = object_id

                    if isinstance(
                        name,
                        str,
                    ):
                        state.board_name = name

                # List ARI
                elif object_id.startswith(
                    "ari:cloud:trello::list/"
                ):

                    state.list_id = object_id

                    if isinstance(
                        name,
                        str,
                    ):
                        state.list_name = name

                # Card ARI
                elif object_id.startswith(
                    "ari:cloud:trello::card/"
                ):

                    state.card_id = object_id

                    if isinstance(
                        name,
                        str,
                    ):
                        state.card_name = name

            # ----------------------------------------------
            # Explicitly inspect nested structures
            # ----------------------------------------------

            for nested_value in value.values():
                visit(
                    nested_value
                )

        elif isinstance(
            value,
            list,
        ):

            for item in value:
                visit(
                    item
                )

    visit(data)


# ============================================================
# OAUTH TOKEN STORAGE
# ============================================================

class InMemoryTokenStorage(
    TokenStorage
):

    def __init__(self):

        self.tokens: (
            OAuthToken | None
        ) = None

        self.client_info: (
            OAuthClientInformationFull | None
        ) = None

    async def get_tokens(
        self,
    ) -> OAuthToken | None:

        return self.tokens

    async def set_tokens(
        self,
        tokens: OAuthToken,
    ) -> None:

        self.tokens = tokens

    async def get_client_info(
        self,
    ) -> OAuthClientInformationFull | None:

        return self.client_info

    async def set_client_info(
        self,
        client_info: OAuthClientInformationFull,
    ) -> None:

        self.client_info = client_info


# ============================================================
# OAUTH CALLBACK
# ============================================================

async def handle_redirect(
    authorization_url: str,
) -> None:

    print()
    print("=" * 80)
    print("OPENING TRELLO AUTHORIZATION")
    print("=" * 80)
    print()

    print("Authorization URL:")
    print(authorization_url)
    print()

    # --------------------------------------------------------
    # Start callback server BEFORE opening browser.
    # --------------------------------------------------------

    start_callback_server()

    try:

        opened = webbrowser.open(
            authorization_url
        )

        if opened:
            print(
                "Browser opened automatically."
            )

        else:
            print(
                "Could not open browser automatically."
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
        "Complete the Trello authorization in your browser."
    )

    print(
        "Waiting for automatic callback..."
    )

    print()


async def handle_callback() -> AuthorizationCodeResult:
    """
    Wait for the browser to redirect to localhost.

    No manual callback URL paste is required.
    """

    global _callback_url

    print("=" * 80)
    print("WAITING FOR OAUTH CALLBACK")
    print("=" * 80)
    print()

    # --------------------------------------------------------
    # Wait without blocking the asyncio event loop.
    # --------------------------------------------------------

    try:

        await asyncio.wait_for(
            asyncio.to_thread(
                _callback_event.wait
            ),
            timeout=300,
        )

    except asyncio.TimeoutError:

        raise RuntimeError(
            "Timed out waiting for Trello OAuth callback."
        )

    callback_url = _callback_url

    if not callback_url:

        raise RuntimeError(
            "OAuth callback was received but URL was empty."
        )

    print(
        "OAuth callback received automatically."
    )

    print()

    parsed = urlparse(
        callback_url
    )

    params = parse_qs(
        parsed.query
    )

    # --------------------------------------------------------
    # OAuth error
    # --------------------------------------------------------

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
            f"OAuth authorization failed: "
            f"{error} - {description}"
        )

    # --------------------------------------------------------
    # Authorization code
    # --------------------------------------------------------

    if "code" not in params:

        raise RuntimeError(
            "No authorization code found in callback."
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

    # --------------------------------------------------------
    # Stop callback server.
    # --------------------------------------------------------

    stop_callback_server()

    return AuthorizationCodeResult(
        code=code,
        state=state,
        iss=iss,
    )


# ============================================================
# JSON HELPERS
# ============================================================

def safe_json(
    value: Any,
) -> str:

    try:

        return json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    except Exception:

        return str(value)


# ============================================================
# JSON SCHEMA
# ============================================================

def dereference_schema(
    root_schema: dict[str, Any],
    node: Any,
    max_depth: int = 10,
) -> Any:

    if max_depth <= 0:
        return node

    if isinstance(
        node,
        dict,
    ):

        if "$ref" in node:

            ref = node["$ref"]

            if (
                isinstance(ref, str)
                and ref.startswith("#/")
            ):

                current: Any = root_schema

                for part in ref[2:].split("/"):

                    part = (
                        part
                        .replace(
                            "~1",
                            "/",
                        )
                        .replace(
                            "~0",
                            "~",
                        )
                    )

                    if not isinstance(
                        current,
                        dict,
                    ):

                        current = None
                        break

                    current = current.get(
                        part
                    )

                if isinstance(
                    current,
                    dict,
                ):

                    resolved = dereference_schema(
                        root_schema,
                        current,
                        max_depth - 1,
                    )

                    siblings = {
                        key: value
                        for key, value in node.items()
                        if key != "$ref"
                    }

                    if (
                        siblings
                        and isinstance(
                            resolved,
                            dict,
                        )
                    ):

                        merged = deepcopy(
                            resolved
                        )

                        merged.update(
                            siblings
                        )

                        return dereference_schema(
                            root_schema,
                            merged,
                            max_depth - 1,
                        )

                    return resolved

        return {
            key: dereference_schema(
                root_schema,
                value,
                max_depth - 1,
            )
            for key, value in node.items()
        }

    if isinstance(
        node,
        list,
    ):

        return [
            dereference_schema(
                root_schema,
                item,
                max_depth - 1,
            )
            for item in node
        ]

    return node


def find_action_property(
    schema: dict[str, Any],
) -> dict[str, Any] | None:

    if not isinstance(
        schema,
        dict,
    ):
        return None

    properties = schema.get(
        "properties"
    )

    if isinstance(
        properties,
        dict,
    ):

        action_schema = properties.get(
            "action"
        )

        if isinstance(
            action_schema,
            dict,
        ):

            return action_schema

    for key in (
        "oneOf",
        "anyOf",
        "allOf",
    ):

        branches = schema.get(
            key
        )

        if isinstance(
            branches,
            list,
        ):

            for branch in branches:

                result = find_action_property(
                    branch
                )

                if result is not None:
                    return result

    return None


def discover_actions(
    raw_schema: dict[str, Any],
    description: str,
) -> list[str]:

    schema = dereference_schema(
        raw_schema,
        raw_schema,
    )

    action_schema = find_action_property(
        schema
    )

    if action_schema:

        enum_values = action_schema.get(
            "enum"
        )

        if isinstance(
            enum_values,
            list,
        ):

            return [
                str(value)
                for value in enum_values
            ]

    actions: list[str] = []

    patterns = [
        r"`([A-Za-z0-9_]+)`\s*:",
        r"\b([A-Za-z0-9_]+)\s*:",
        r"\baction\s*=\s*[\"']([^\"']+)[\"']",
    ]

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            description,
            flags=re.IGNORECASE,
        ):

            action = match.group(1)

            if action not in actions:

                actions.append(
                    action
                )

    return actions


def branch_matches_action(
    root_schema: dict[str, Any],
    node: Any,
    action: str,
) -> bool:

    node = dereference_schema(
        root_schema,
        node,
    )

    if not isinstance(
        node,
        dict,
    ):
        return False

    properties = node.get(
        "properties"
    )

    if not isinstance(
        properties,
        dict,
    ):
        return False

    action_schema = properties.get(
        "action"
    )

    if not isinstance(
        action_schema,
        dict,
    ):
        return False

    enum_values = action_schema.get(
        "enum"
    )

    if isinstance(
        enum_values,
        list,
    ):

        return action in enum_values

    return (
        action_schema.get("const")
        == action
    )


def find_action_branch(
    root_schema: dict[str, Any],
    node: Any,
    action: str,
) -> dict[str, Any] | None:

    node = dereference_schema(
        root_schema,
        node,
    )

    if not isinstance(
        node,
        dict,
    ):
        return None

    if branch_matches_action(
        root_schema,
        node,
        action,
    ):
        return node

    for key in (
        "oneOf",
        "anyOf",
        "allOf",
    ):

        branches = node.get(
            key
        )

        if isinstance(
            branches,
            list,
        ):

            for branch in branches:

                result = find_action_branch(
                    root_schema,
                    branch,
                    action,
                )

                if result is not None:
                    return result

    for key in (
        "$defs",
        "definitions",
    ):

        definitions = node.get(
            key
        )

        if isinstance(
            definitions,
            dict,
        ):

            for definition in definitions.values():

                result = find_action_branch(
                    root_schema,
                    definition,
                    action,
                )

                if result is not None:
                    return result

    return None


def get_action_description(
    description: str,
    action: str,
    all_actions: list[str],
) -> str:

    if not description:
        return ""

    positions = []

    for candidate in all_actions:

        pattern = (
            rf"`?{re.escape(candidate)}`?\s*:"
        )

        match = re.search(
            pattern,
            description,
            flags=re.IGNORECASE,
        )

        if match:

            positions.append(
                (
                    match.start(),
                    candidate,
                )
            )

    if not positions:
        return description

    positions.sort()

    current_index = None

    for index, (
        _,
        candidate,
    ) in enumerate(positions):

        if (
            candidate.lower()
            == action.lower()
        ):

            current_index = index
            break

    if current_index is None:
        return description

    start = positions[
        current_index
    ][0]

    if (
        current_index + 1
        < len(positions)
    ):

        end = positions[
            current_index + 1
        ][0]

    else:

        end = len(description)

    return description[
        start:end
    ].strip()


def extract_properties_mentioned_in_description(
    schema: dict[str, Any],
    action_description: str,
) -> set[str]:

    properties = schema.get(
        "properties"
    )

    if not isinstance(
        properties,
        dict,
    ):
        return set()

    found: set[str] = set()

    for property_name in properties:

        if property_name == "action":
            continue

        pattern = (
            rf"\b{re.escape(property_name)}\b"
        )

        if re.search(
            pattern,
            action_description,
            flags=re.IGNORECASE,
        ):

            found.add(
                property_name
            )

    return found


def build_action_schema(
    raw_schema: dict[str, Any],
    action: str,
    all_actions: list[str],
    tool_description: str,
) -> dict[str, Any]:

    resolved_root = dereference_schema(
        raw_schema,
        raw_schema,
    )

    branch = find_action_branch(
        raw_schema,
        resolved_root,
        action,
    )

    if branch is not None:

        branch = dereference_schema(
            raw_schema,
            branch,
        )

        properties = branch.get(
            "properties",
            {},
        )

        required = branch.get(
            "required",
            [],
        )

        if isinstance(
            properties,
            dict,
        ):

            result_properties = {}

            for name, definition in properties.items():

                if name == "action":
                    continue

                result_properties[name] = deepcopy(
                    definition
                )

            return {
                "type": "object",
                "properties": result_properties,
                "required": [
                    name
                    for name in required
                    if name != "action"
                ],
                "additionalProperties": False,
            }

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    action_description = get_action_description(
        tool_description,
        action,
        all_actions,
    )

    properties = resolved_root.get(
        "properties",
        {},
    )

    if not isinstance(
        properties,
        dict,
    ):
        properties = {}

    mentioned = (
        extract_properties_mentioned_in_description(
            resolved_root,
            action_description,
        )
    )

    required_from_root = resolved_root.get(
        "required",
        [],
    )

    if not isinstance(
        required_from_root,
        list,
    ):
        required_from_root = []

    selected = set(
        mentioned
    )

    for required_name in required_from_root:

        if (
            required_name != "action"
            and required_name in mentioned
        ):

            selected.add(
                required_name
            )

    result_properties = {}

    for property_name in selected:

        definition = properties.get(
            property_name
        )

        if definition is not None:

            result_properties[
                property_name
            ] = deepcopy(
                definition
            )

    return {
        "type": "object",
        "properties": result_properties,
        "required": [
            name
            for name in required_from_root
            if (
                name in selected
                and name != "action"
            )
        ],
        "additionalProperties": False,
    }


# ============================================================
# OPENAI SCHEMA SANITIZER
# ============================================================

def sanitize_openai_schema(
    schema: dict[str, Any],
) -> dict[str, Any]:

    if not isinstance(
        schema,
        dict,
    ):

        return {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

    schema = deepcopy(
        schema
    )

    schema.pop(
        "$schema",
        None,
    )

    return schema


# ============================================================
# MCP → OPENAI VIRTUAL TOOLS
# ============================================================

def create_virtual_tools(
    mcp_tools: list[Any],
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
]:

    openai_tools = []

    virtual_tool_map = {}

    for mcp_tool in mcp_tools:

        tool_name = mcp_tool.name

        description = (
            getattr(
                mcp_tool,
                "description",
                None,
            )
            or ""
        )

        raw_schema = (
            getattr(
                mcp_tool,
                "input_schema",
                None,
            )
            or {}
        )

        actions = discover_actions(
            raw_schema,
            description,
        )

        # ====================================================
        # ACTION TOOL
        # ====================================================

        if actions:

            for action in actions:

                virtual_name = (
                    f"{tool_name}_{action}"
                )

                action_schema = build_action_schema(
                    raw_schema,
                    action,
                    actions,
                    description,
                )

                action_schema = (
                    sanitize_openai_schema(
                        action_schema
                    )
                )

                action_description = (
                    get_action_description(
                        description,
                        action,
                        actions,
                    )
                )

                openai_tools.append(
                    {
                        "type": "function",
                        "name": virtual_name,
                        "description": (
                            f"MCP tool: {tool_name}\n"
                            f"Action: {action}\n\n"
                            f"{action_description}"
                        ),
                        "parameters": action_schema,
                        "strict": False,
                    }
                )

                virtual_tool_map[
                    virtual_name
                ] = {
                    "mcp_tool_name": tool_name,
                    "action": action,
                    "original_schema": raw_schema,
                }

        # ====================================================
        # NORMAL TOOL
        # ====================================================

        else:

            raw_schema = (
                sanitize_openai_schema(
                    raw_schema
                )
            )

            openai_tools.append(
                {
                    "type": "function",
                    "name": tool_name,
                    "description": description,
                    "parameters": raw_schema,
                    "strict": False,
                }
            )

            virtual_tool_map[
                tool_name
            ] = {
                "mcp_tool_name": tool_name,
                "action": None,
                "original_schema": raw_schema,
            }

    return (
        openai_tools,
        virtual_tool_map,
    )


# ============================================================
# PRINT TOOLS
# ============================================================

def print_virtual_tools(
    tools: list[dict[str, Any]],
) -> None:

    print()
    print("=" * 80)
    print("LLM-FACING TOOLS")
    print("=" * 80)

    for index, tool in enumerate(
        tools,
        start=1,
    ):

        print(
            f"{index:02d}. {tool['name']}"
        )

    print("=" * 80)
    print()


# ============================================================
# MCP RESULT
# ============================================================

def extract_mcp_result(
    result: Any,
) -> tuple[
    bool,
    str,
]:

    is_error = bool(
        getattr(
            result,
            "isError",
            False,
        )
    )

    content = getattr(
        result,
        "content",
        None,
    )

    if content is None:

        return (
            is_error,
            safe_json(result),
        )

    pieces = []

    for item in content:

        item_type = getattr(
            item,
            "type",
            None,
        )

        if item_type == "text":

            pieces.append(
                str(
                    getattr(
                        item,
                        "text",
                        "",
                    )
                )
            )

        else:

            pieces.append(
                safe_json(item)
            )

    return (
        is_error,
        "\n".join(
            pieces
        ),
    )


# ============================================================
# PLACEHOLDER PROTECTION
# ============================================================

PLACEHOLDER_VALUES = {
    "",
    "unused",
    "omit",
    "none",
    "null",
    "undefined",
    "unknown",
    "n/a",
    "na",
    "?",
    "<cursor>",
    "<workspaceid>",
    "<workspaceId>",
    "<boardid>",
    "<boardId>",
    "<listid>",
    "<listId>",
    "<cardid>",
    "<cardId>",
    "<memberid>",
    "<memberId>",
}


def is_placeholder(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        str,
    ):
        return False

    normalized = value.strip().lower()

    if normalized in PLACEHOLDER_VALUES:
        return True

    if (
        normalized.startswith("<")
        and normalized.endswith(">")
    ):
        return True

    return False


def clean_arguments(
    arguments: dict[str, Any],
) -> dict[str, Any]:

    cleaned = {}

    for key, value in arguments.items():

        if is_placeholder(
            value
        ):
            continue

        cleaned[key] = value

    return cleaned


# ============================================================
# GENERIC MCP INVOCATION
# ============================================================

async def invoke_virtual_tool(
    client: Client,
    virtual_tool_name: str,
    arguments: dict[str, Any],
    virtual_tool_map: dict[str, dict[str, Any]],
) -> tuple[
    bool,
    str,
]:

    mapping = virtual_tool_map.get(
        virtual_tool_name
    )

    if mapping is None:

        return (
            True,
            f"Unknown virtual tool: "
            f"{virtual_tool_name}",
        )

    mcp_tool_name = mapping[
        "mcp_tool_name"
    ]

    action = mapping[
        "action"
    ]

    arguments = clean_arguments(
        arguments
    )

    # --------------------------------------------------------
    # Inject action
    # --------------------------------------------------------

    if action is not None:

        arguments["action"] = action

    print()
    print("-" * 80)
    print("MCP CALL")
    print("-" * 80)

    print(
        f"Virtual tool : "
        f"{virtual_tool_name}"
    )

    print(
        f"MCP tool     : "
        f"{mcp_tool_name}"
    )

    if action:

        print(
            f"Action       : "
            f"{action}"
        )

    print("Arguments:")

    print(
        safe_json(arguments)
    )

    print("-" * 80)

    try:

        result = await client.call_tool(
            mcp_tool_name,
            arguments=arguments,
        )

    except Exception as exc:

        return (
            True,
            (
                "MCP Python exception: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

    is_error, result_text = (
        extract_mcp_result(
            result
        )
    )

    if is_error:

        print(
            "MCP returned an ERROR."
        )

        print(
            result_text
        )

    else:

        print(
            "MCP call succeeded."
        )

    return (
        is_error,
        result_text,
    )


# ============================================================
# FAILURE FINGERPRINT
# ============================================================

def make_failure_fingerprint(
    tool_name: str,
    arguments: dict[str, Any],
    result: str,
) -> str:

    return (
        f"{tool_name}|"
        f"{json.dumps(arguments, sort_keys=True)}|"
        f"{result}"
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an intelligent Trello assistant.

You operate as a stateful conversational agent.

IMPORTANT RULES:

1. Choose tools dynamically.

2. NEVER invent Trello IDs.

3. NEVER invent ARIs.

4. NEVER use placeholder values such as:
   - unused
   - omit
   - null
   - ?
   - <workspaceId>
   - <boardId>

5. If an operation requires an ID, use a real ID obtained
   from a previous successful tool call or from the current
   conversation.

6. Remember useful information from previous tool results.

7. The application provides a CURRENT AGENT STATE below.

8. Use the current agent state whenever it contains the
   information needed for the user's request.

9. If the user says:
      "that board"
      "that list"
      "the card"
      "my project"

   use the relevant context from the current conversation
   and state.

10. Do not claim an operation succeeded unless the MCP
    server actually returned success.

11. If a tool call fails, do not repeat the same failed call.

12. For dependent operations, proceed step by step.

Example:

    workspace
       ↓
    board
       ↓
    list
       ↓
    card

13. Prefer one tool call at a time.

14. When the user's current request is complete, answer
    naturally and briefly.

15. Do not expose internal implementation details.

16. The user may send another request after your answer.
    Maintain context across those requests.
"""


# ============================================================
# PROCESS ONE USER MESSAGE
# ============================================================

async def process_user_message(
    client: Client,
    state: AgentState,
    user_message: str,
    openai_tools: list[dict[str, Any]],
    virtual_tool_map: dict[str, dict[str, Any]],
) -> None:

    # --------------------------------------------------------
    # Add user message to persistent conversation
    # --------------------------------------------------------

    state.conversation.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # --------------------------------------------------------
    # Agent loop for THIS request
    # --------------------------------------------------------

    for turn in range(
        1,
        MAX_AGENT_TURNS + 1,
    ):

        state.total_turns += 1

        print()
        print("=" * 80)
        print(
            f"AGENT TURN "
            f"{turn}"
        )
        print("=" * 80)

        # ----------------------------------------------------
        # State injected into instructions
        # ----------------------------------------------------

        current_state = state_summary(
            state
        )

        instructions = (
            SYSTEM_PROMPT
            + "\n\n"
            + "CURRENT AGENT STATE:\n"
            + current_state
        )

        # ----------------------------------------------------
        # Ask LLM
        # ----------------------------------------------------

        try:

            response = (
                OPENAI_CLIENT.responses.create(
                    model=MODEL,
                    instructions=instructions,
                    tools=openai_tools,
                    input=state.conversation,
                    parallel_tool_calls=False,
                )
            )

        except Exception as exc:

            print()
            print(
                "OpenAI API error:"
            )

            print(
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            return

        # ----------------------------------------------------
        # Save model output in conversation state
        # ----------------------------------------------------

        state.conversation.extend(
            response.output
        )

        # ----------------------------------------------------
        # Find tool calls
        # ----------------------------------------------------

        tool_calls = [
            item
            for item in response.output
            if getattr(
                item,
                "type",
                None,
            ) == "function_call"
        ]

        # ----------------------------------------------------
        # No tool calls = final answer
        # ----------------------------------------------------

        if not tool_calls:

            print()
            print("=" * 80)
            print("ASSISTANT")
            print("=" * 80)
            print()

            print(
                response.output_text
            )

            return

        # ----------------------------------------------------
        # Execute tool calls
        # ----------------------------------------------------

        for tool_call in tool_calls:

            virtual_tool_name = (
                tool_call.name
            )

            try:

                arguments = json.loads(
                    tool_call.arguments
                )

            except json.JSONDecodeError:

                tool_result = (
                    "ERROR: Invalid JSON "
                    "arguments generated by model."
                )

                state.conversation.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": tool_result,
                    }
                )

                continue

            if not isinstance(
                arguments,
                dict,
            ):

                arguments = {}

            # ------------------------------------------------
            # Remove placeholders
            # ------------------------------------------------

            arguments = clean_arguments(
                arguments
            )

            # ------------------------------------------------
            # Check duplicate failed call
            # ------------------------------------------------

            prefix = (
                f"{virtual_tool_name}|"
                f"{json.dumps(arguments, sort_keys=True)}|"
            )

            repeated = any(
                fingerprint.startswith(
                    prefix
                )
                for fingerprint
                in state.failed_calls
            )

            if repeated:

                tool_result = (
                    "ERROR: This exact tool call "
                    "already failed earlier. "
                    "Do not repeat it. "
                    "Use another strategy."
                )

                state.conversation.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": tool_result,
                    }
                )

                continue

            # ------------------------------------------------
            # Execute MCP
            # ------------------------------------------------

            (
                is_error,
                result_text,
            ) = await invoke_virtual_tool(
                client=client,
                virtual_tool_name=virtual_tool_name,
                arguments=arguments,
                virtual_tool_map=virtual_tool_map,
            )

            # ------------------------------------------------
            # Update state from successful result
            # ------------------------------------------------

            if not is_error:

                update_state_from_result(
                    state,
                    result_text,
                )

                print()
                print(
                    "CURRENT STATE:"
                )

                print(
                    state_summary(
                        state
                    )
                )

            # ------------------------------------------------
            # Store failures
            # ------------------------------------------------

            if is_error:

                fingerprint = (
                    make_failure_fingerprint(
                        virtual_tool_name,
                        arguments,
                        result_text,
                    )
                )

                state.failed_calls.add(
                    fingerprint
                )

            # ------------------------------------------------
            # Return MCP result to LLM
            # ------------------------------------------------

            if is_error:

                tool_output = (
                    "MCP TOOL ERROR:\n"
                    + result_text
                )

            else:

                tool_output = (
                    "MCP TOOL SUCCESS:\n"
                    + result_text
                )

            state.conversation.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": tool_output,
                }
            )

    print()

    print(
        "Maximum agent turns reached."
    )


# ============================================================
# CONVERSATION LOOP
# ============================================================

async def conversation_loop(
    client: Client,
    mcp_tools: list[Any],
) -> None:

    # --------------------------------------------------------
    # Create virtual tools ONCE
    # --------------------------------------------------------

    (
        openai_tools,
        virtual_tool_map,
    ) = create_virtual_tools(
        mcp_tools
    )

    print_virtual_tools(
        openai_tools
    )

    # --------------------------------------------------------
    # Create persistent state
    # --------------------------------------------------------

    state = AgentState()

    print()
    print("=" * 80)
    print("STATEFUL TRELLO AGENT")
    print("=" * 80)
    print()

    print(
        "You can continue the conversation."
    )

    print(
        "Type 'exit' or 'quit' to stop."
    )

    print()

    # ========================================================
    # USER CONVERSATION LOOP
    # ========================================================

    while True:

        try:

            user_message = input(
                "You > "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt,
        ):

            print()

            print(
                "Goodbye!"
            )

            break

        if not user_message:
            continue

        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        if user_message.lower() in {
            "exit",
            "quit",
            "bye",
        }:

            print()

            print(
                "Goodbye!"
            )

            break

        # ----------------------------------------------------
        # Optional state inspection
        # ----------------------------------------------------

        if user_message.lower() == "/state":

            print()
            print("=" * 80)
            print("CURRENT STATE")
            print("=" * 80)

            print(
                state_summary(
                    state
                )
            )

            print()

            continue

        # ----------------------------------------------------
        # Process request
        # ----------------------------------------------------

        await process_user_message(
            client=client,
            state=state,
            user_message=user_message,
            openai_tools=openai_tools,
            virtual_tool_map=virtual_tool_map,
        )

        print()


# ============================================================
# MAIN
# ============================================================

async def main():

    print()
    print("=" * 80)
    print("TRELLO MCP AGENT")
    print("=" * 80)
    print()

    # --------------------------------------------------------
    # Check OpenAI API key
    # --------------------------------------------------------

    if not os.getenv(
        "OPENAI_API_KEY"
    ):

        raise RuntimeError(
            "OPENAI_API_KEY environment variable "
            "is not set."
        )

    # --------------------------------------------------------
    # OAuth
    # --------------------------------------------------------

    oauth_provider = OAuthClientProvider(
        server_url=MCP_SERVER_URL,

        client_metadata=OAuthClientMetadata(
            client_name="Trello MCP Agent",

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

            scope="",
        ),

        storage=InMemoryTokenStorage(),

        redirect_handler=handle_redirect,

        callback_handler=handle_callback,
    )

    # --------------------------------------------------------
    # HTTP client
    # --------------------------------------------------------

    async with httpx2.AsyncClient(
        auth=oauth_provider,
        timeout=httpx2.Timeout(
            30.0,
            read=300.0,
        ),
    ) as http_client:

        # ----------------------------------------------------
        # MCP transport
        # ----------------------------------------------------

        transport = streamable_http_client(
            MCP_SERVER_URL,
            http_client=http_client,
        )

        # ----------------------------------------------------
        # MCP client
        # ----------------------------------------------------

        async with Client(
            transport
        ) as client:

            print()

            print(
                "Connected to Trello MCP Server!"
            )

            # ------------------------------------------------
            # Discover tools
            # ------------------------------------------------

            result = await client.list_tools()

            mcp_tools = result.tools

            print(
                f"Discovered "
                f"{len(mcp_tools)} MCP tools."
            )

            print()

            for tool in mcp_tools:

                print(
                    f"  - {tool.name}"
                )

            print()

            # ------------------------------------------------
            # Start conversation
            # ------------------------------------------------

            await conversation_loop(
                client=client,
                mcp_tools=mcp_tools,
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    finally:

        # Make sure callback server is closed
        # even if the application exits unexpectedly.

        stop_callback_server()
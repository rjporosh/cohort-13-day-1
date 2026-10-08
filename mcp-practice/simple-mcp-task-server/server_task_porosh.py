from pathlib import Path
import json
import os
import sys
import datetime
from typing import Any

from mcp.server.mcpserver import MCPServer


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "data" / "tasks.json"

mcp = MCPServer(
    "Task Management Server",
    version="1.0.0",
)


# ============================================================
# JSON DATABASE HELPERS
# ============================================================

def load_database() -> dict[str, Any]:
    """Load the JSON database from disk."""
    if not DATABASE_FILE.exists():
        return {"tasks": []}

    with DATABASE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_database(database: dict[str, Any]) -> None:
    """Save the JSON database to disk."""
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATABASE_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            database,
            file,
            indent=2,
            ensure_ascii=False,
        )


def get_next_task_id(
    tasks: list[dict[str, Any]],
) -> int:
    """Generate the next numeric task ID."""
    return max(
        (task["id"] for task in tasks),
        default=0,
    ) + 1


def find_task(
    tasks: list[dict[str, Any]],
    task_id: int,
) -> dict[str, Any] | None:
    """Find a task by ID."""
    return next(
        (
            task
            for task in tasks
            if task["id"] == task_id
        ),
        None,
    )


# ============================================================
# MCP TOOLS
# ============================================================

@mcp.tool()
def create_task(
    title: str,
    description: str = "",
) -> dict[str, Any]:
    """Create a new task."""
    database = load_database()
    tasks = database["tasks"]

    task = {
        "id": get_next_task_id(tasks),
        "title": title,
        "description": description,
        "status": "pending",
        "created_at": datetime.datetime.now().isoformat(),
    }

    tasks.append(task)
    save_database(database)

    return {
        "success": True,
        "message": "Task created successfully.",
        "task": task,
    }


@mcp.tool()
def get_task(
    task_id: int,
) -> dict[str, Any]:
    """Get a task by its ID."""
    database = load_database()

    task = find_task(
        database["tasks"],
        task_id,
    )

    if task is None:
        return {
            "success": False,
            "message": f"Task {task_id} was not found.",
        }

    return {
        "success": True,
        "task": task,
    }


@mcp.tool()
def list_tasks(
    status: str = "",
) -> dict[str, Any]:
    """List all tasks, optionally filtered by status."""
    database = load_database()
    tasks = database["tasks"]

    if status:
        tasks = [
            task
            for task in tasks
            if task["status"].lower()
            == status.lower()
        ]

    return {
        "success": True,
        "count": len(tasks),
        "tasks": tasks,
    }


@mcp.tool()
def update_task(
    task_id: int,
    title: str = "",
    description: str = "",
    status: str = "",
) -> dict[str, Any]:
    """Update an existing task."""
    database = load_database()

    task = find_task(
        database["tasks"],
        task_id,
    )

    if task is None:
        return {
            "success": False,
            "message": f"Task {task_id} was not found.",
        }

    if title:
        task["title"] = title

    if description:
        task["description"] = description

    if status:
        task["status"] = status

    save_database(database)

    return {
        "success": True,
        "message": "Task updated successfully.",
        "task": task,
    }


@mcp.tool()
def delete_task(
    task_id: int,
) -> dict[str, Any]:
    """Delete a task by its ID."""
    database = load_database()

    task = find_task(
        database["tasks"],
        task_id,
    )

    if task is None:
        return {
            "success": False,
            "message": f"Task {task_id} was not found.",
        }

    database["tasks"].remove(task)
    save_database(database)

    return {
        "success": True,
        "message": "Task deleted successfully.",
        "task": task,
    }


# ============================================================
# AI CHAT ASSISTANT — OpenAI-powered task query interface
# ============================================================

def _build_task_context() -> str:
    """
    Build a plain-text context string describing all current
    tasks so the AI can answer questions about them.
    """
    database = load_database()
    tasks = database["tasks"]

    today = datetime.date.today().isoformat()

    if not tasks:
        return f"Today's date is {today}. There are no tasks in the database."

    lines = [
        f"Today's date is {today}.",
        f"Total tasks: {len(tasks)}.",
        "",
        "Task list:",
    ]

    for task in tasks:
        created = task.get("created_at", "unknown date")
        # Show only the date portion if ISO datetime
        if "T" in str(created):
            created = created.split("T")[0]

        is_today = created == today
        today_tag = " [created today]" if is_today else ""

        lines.append(
            f"  - ID {task['id']}: \"{task['title']}\" | "
            f"Status: {task['status']} | "
            f"Created: {created}{today_tag} | "
            f"Description: {task.get('description', 'N/A')}"
        )

    # Quick summary stats
    completed = sum(
        1 for t in tasks if t["status"].lower() == "completed"
    )
    pending = sum(
        1 for t in tasks if t["status"].lower() == "pending"
    )
    in_progress = sum(
        1 for t in tasks if t["status"].lower() == "in_progress"
    )
    tasks_today = sum(
        1 for t in tasks
        if str(t.get("created_at", "")).startswith(today)
    )

    lines += [
        "",
        f"Summary — Completed: {completed} | "
        f"Pending: {pending} | "
        f"In Progress: {in_progress} | "
        f"Created today: {tasks_today}",
    ]

    return "\n".join(lines)


def run_chat_assistant() -> None:
    """
    Launch an interactive OpenAI-powered chatbox in the terminal.

    Users can ask natural-language questions like:
      - "How many tasks do I have today?"
      - "What tasks are completed?"
      - "What's the status of all tasks?"
      - "How many pending tasks are there?"

    The assistant always reads the live task database before
    answering, so answers reflect the current state.

    Type 'exit' or 'quit' to leave the chat.
    """

    try:
        from openai import OpenAI
    except ImportError:
        print(
            "\n[ERROR] openai package is not installed.\n"
            "Run: pip install openai\n"
        )
        return

    api_key = os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        print(
            "\n[ERROR] OPENAI_API_KEY environment variable is not set.\n"
            "Export it before running:\n"
            "  export OPENAI_API_KEY='sk-...'\n"
        )
        return

    client = OpenAI(api_key=api_key)

    SYSTEM_PROMPT = (
        "You are a helpful task management assistant. "
        "The user will ask questions about their tasks. "
        "You will receive a live snapshot of their task database "
        "in every message. Answer concisely and clearly. "
        "If the user asks to create, update, or delete a task, "
        "explain that those actions must be done through the MCP tools "
        "and guide them on what to say."
    )

    print()
    print("=" * 70)
    print("  TASK ASSISTANT — AI Chat (powered by OpenAI)")
    print("=" * 70)
    print("  Ask anything about your tasks in natural language.")
    print("  Examples:")
    print("    • How many tasks do I have today?")
    print("    • What tasks are completed?")
    print("    • What is the status of all my tasks?")
    print("    • How many pending tasks are left?")
    print()
    print("  Type 'exit' or 'quit' to return to the MCP server.")
    print("=" * 70)
    print()

    conversation_history: list[dict[str, str]] = []

    while True:

        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n[Chat closed]")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye", "q"}:
            print("\n[Chat closed. MCP server continues running.]\n")
            break

        # Inject fresh task context into every user message
        task_context = _build_task_context()

        augmented_message = (
            f"{user_input}\n\n"
            f"--- Current Task Database Snapshot ---\n"
            f"{task_context}"
        )

        conversation_history.append(
            {"role": "user", "content": augmented_message}
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *conversation_history,
                ],
                temperature=0.3,
                max_tokens=512,
            )

            assistant_reply = (
                response.choices[0].message.content.strip()
            )

            # Store only the raw user message (without task dump)
            # to keep conversation history clean
            conversation_history[-1] = {
                "role": "user",
                "content": user_input,
            }
            conversation_history.append(
                {"role": "assistant", "content": assistant_reply}
            )

            print(f"\nAssistant: {assistant_reply}\n")

        except Exception as exc:
            print(f"\n[AI Error] {type(exc).__name__}: {exc}\n")
            # Remove the failed message from history
            conversation_history.pop()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    # If called with --chat flag, launch the AI chat assistant
    # instead of the MCP server.
    #
    # Usage:
    #   python server_task_porosh.py --chat
    #
    # For MCP server mode (default):
    #   python server_task_porosh.py

    if "--chat" in sys.argv:
        run_chat_assistant()
    else:
        mcp.run()

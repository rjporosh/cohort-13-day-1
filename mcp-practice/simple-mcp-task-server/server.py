from pathlib import Path
import json
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
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    mcp.run()

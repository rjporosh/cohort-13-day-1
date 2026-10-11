from pathlib import Path
import json
from typing import Any

from mcp.server.mcpserver import MCPServer


# ============================================================
# Database Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "data" / "tasks.json"


# ============================================================
# MCP Server
# ============================================================

mcp = MCPServer(
    "Task Management Server",
    version="1.0.0"
)


# ============================================================
# Helper Functions
# ============================================================

def load_tasks() -> list[dict[str, Any]]:
    """
    Load all tasks from the JSON database.

    Supports both formats:

    1. Direct list:
       [
           {"id": 1, "title": "..."}
       ]

    2. Wrapped object:
       {
           "tasks": [
               {"id": 1, "title": "..."}
           ]
       }
    """

    if not DATABASE_FILE.exists():
        return []

    with open(
        DATABASE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # If JSON is already a list
    if isinstance(data, list):
        return data

    # If JSON is wrapped inside {"tasks": [...]}
    if isinstance(data, dict):
        return data.get("tasks", [])

    return []


def save_tasks(tasks: list[dict[str, Any]]) -> None:
    """
    Save all tasks to the JSON database.
    """

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        DATABASE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            tasks,
            file,
            indent=4,
            ensure_ascii=False
        )


def get_next_id(tasks: list[dict[str, Any]]) -> int:
    """
    Generate the next available task ID.
    """

    if not tasks:
        return 1

    return max(
        task["id"]
        for task in tasks
    ) + 1


def find_task(
    tasks: list[dict[str, Any]],
    task_id: int
) -> dict[str, Any] | None:

    for task in tasks:

        if task["id"] == task_id:
            return task

    return None


# ============================================================
# MCP Tools
# ============================================================

@mcp.tool()
def create_task(
    title: str,
    description: str = "",
    status: str = "pending"
) -> dict[str, Any]:
    """
    Create a new task and save it to the task database.

    Args:
        title:
            Short title of the task.

        description:
            Optional detailed description of the task.

        status:
            Initial task status. Defaults to 'pending'.

    Returns:
        The newly created task.
    """

    tasks = load_tasks()

    task = {
        "id": get_next_id(tasks),
        "title": title,
        "description": description,
        "status": status
    }

    tasks.append(task)

    save_tasks(tasks)

    return task


@mcp.tool()
def get_task(
    task_id: int
) -> dict[str, Any] | None:
    """
    Retrieve a single task by its ID.

    Args:
        task_id:
            Unique ID of the task.

    Returns:
        The requested task, or None if it does not exist.
    """

    tasks = load_tasks()

    return find_task(
        tasks,
        task_id
    )


@mcp.tool()
def list_tasks() -> list[dict[str, Any]]:
    """
    Retrieve all tasks from the task database.

    Returns:
        A list containing all tasks.
    """

    return load_tasks()


@mcp.tool()
def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None
) -> dict[str, Any] | None:
    """
    Update one or more fields of an existing task.

    Args:
        task_id:
            Unique ID of the task to update.

        title:
            New task title. Leave empty to keep the existing title.

        description:
            New task description. Leave empty to keep the existing description.

        status:
            New task status. Leave empty to keep the existing status.

    Returns:
        The updated task, or None if the task does not exist.
    """

    tasks = load_tasks()

    task = find_task(
        tasks,
        task_id
    )

    if task is None:
        return None

    if title is not None:
        task["title"] = title

    if description is not None:
        task["description"] = description

    if status is not None:
        task["status"] = status

    save_tasks(tasks)

    return task


@mcp.tool()
def delete_task(
    task_id: int
) -> dict[str, Any] | None:
    """
    Delete a task from the task database.

    Args:
        task_id:
            Unique ID of the task to delete.

    Returns:
        The deleted task, or None if the task does not exist.
    """

    tasks = load_tasks()

    task = find_task(
        tasks,
        task_id
    )

    if task is None:
        return None

    tasks.remove(task)
    save_tasks(tasks)
    return task

# ============================================================
# Server Entry Point
# ============================================================
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
    )
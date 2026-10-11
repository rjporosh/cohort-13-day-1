from pathlib import Path
import json
from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "data" / "tasks.json"

mcp = MCPServer("Task Management Server", version="1.0.0")


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
        json.dump(database, file, indent=2, ensure_ascii=False)


def get_next_task_id(tasks: list[dict[str, Any]]) -> int:
    """Generate the next numeric task ID."""
    return max((task["id"] for task in tasks), default=0) + 1


def find_task(tasks: list[dict[str, Any]], task_id: int) -> dict[str, Any] | None:
    """Find a task by ID."""
    return next((task for task in tasks if task["id"] == task_id), None)


@mcp.tool(
    title="Create Task",
    description=("Create a new task in the task database. The new task receives a unique numeric ID and starts with a 'pending' status."),
    annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False),
)
def create_task(
    title: Annotated[str, Field(description="Short, meaningful title for the task. Example: 'Prepare project proposal'.")],
    description: Annotated[str, Field(description="Optional detailed explanation of what the task is about or what needs to be done.")] = "",
) -> dict[str, Any]:
    """Create a new task."""
    database = load_database()
    tasks = database["tasks"]
    task = {"id": get_next_task_id(tasks), "title": title, "description": description, "status": "pending"}
    tasks.append(task)
    save_database(database)
    return {"success": True, "message": "Task created successfully.", "task": task}


@mcp.tool(
    title="Get Task",
    description=("Retrieve one task from the task database using its numeric task ID. Returns the complete task details."),
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
)
def get_task(
    task_id: Annotated[int, Field(description="Numeric ID of the task to retrieve. Use an ID returned by create_task or list_tasks.")],
) -> dict[str, Any]:
    """Get a task by its ID."""
    database = load_database()
    task = find_task(database["tasks"], task_id)
    if task is None:
        return {"success": False, "message": f"Task {task_id} was not found."}
    return {"success": True, "task": task}


@mcp.tool(
    title="List Tasks",
    description=("List tasks currently stored in the task database. Optionally filter the results by task status. Returns the matching tasks and their total count."),
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
)
def list_tasks(
    status: Annotated[str, Field(description="Optional status filter. Leave empty to return all tasks. If provided, only tasks whose status matches this value are returned.")] = "",
) -> dict[str, Any]:
    """List all tasks, optionally filtered by status."""
    database = load_database()
    tasks = database["tasks"]
    if status:
        tasks = [task for task in tasks if task["status"].lower() == status.lower()]
    return {"success": True, "count": len(tasks), "tasks": tasks}


@mcp.tool(
    title="Update Task",
    description=("Update an existing task. Use the task ID to identify the task, then provide one or more new values for its title, description, or status."),
    annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False),
)
def update_task(
    task_id: Annotated[int, Field(description="Numeric ID of the task to update. Use an ID returned by create_task or list_tasks.")],
    title: Annotated[str, Field(description="New task title. Leave empty if the current title should remain unchanged.")] = "",
    description: Annotated[str, Field(description="New task description. Leave empty if the current description should remain unchanged.")] = "",
    status: Annotated[str, Field(description="New task status. Leave empty if the current status should remain unchanged.")] = "",
) -> dict[str, Any]:
    """Update an existing task."""
    database = load_database()
    task = find_task(database["tasks"], task_id)
    if task is None:
        return {"success": False, "message": f"Task {task_id} was not found."}
    if title:
        task["title"] = title
    if description:
        task["description"] = description
    if status:
        task["status"] = status
    save_database(database)
    return {"success": True, "message": "Task updated successfully.", "task": task}


@mcp.tool(
    title="Delete Task",
    description=("Permanently remove a task from the task database using its numeric ID. The deleted task is returned in the response for confirmation."),
    annotations=ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=True, open_world_hint=False),
)
def delete_task(
    task_id: Annotated[int, Field(description="Numeric ID of the task to permanently delete. Use an ID returned by create_task or list_tasks.")],
) -> dict[str, Any]:
    """Delete a task by its ID."""
    database = load_database()
    task = find_task(database["tasks"], task_id)
    if task is None:
        return {"success": False, "message": f"Task {task_id} was not found."}
    database["tasks"].remove(task)
    save_database(database)
    return {"success": True, "message": "Task deleted successfully.", "task": task}


if __name__ == "__main__":
    mcp.run()

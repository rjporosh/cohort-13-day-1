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

# Voice mode language: "en-US" = English, "bn-BD" = Bangla
VOICE_LANGUAGE = "en-US"

# How many previous messages to remember in chat history
MAX_HISTORY_MESSAGES = 20

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

SYSTEM_PROMPT = (
    "You are a helpful task management assistant. "
    "You will receive a live snapshot of the user's task database "
    "with every message. Answer concisely and clearly using only "
    "that snapshot. If the user asks you to create, update, or "
    "delete a task, explain that those actions must be done "
    "through the MCP tools."
)


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


def _get_openai_client():
    """Create an OpenAI client, or raise a clear error."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "openai package is not installed. Run: pip install openai"
        )

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Export it first:  export OPENAI_API_KEY='sk-...'\n"
            "(Windows CMD:  set OPENAI_API_KEY=sk-...)"
        )

    return OpenAI(api_key=api_key)


def _answer_question(
    question: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    """
    Send a question + live task snapshot to OpenAI,
    return the assistant's reply as text.
    """
    client = _get_openai_client()

    augmented = (
        f"{question}\n\n"
        f"--- Current Task Database Snapshot ---\n"
        f"{_build_task_context()}"
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": augmented})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()


# ------------------------------------------------------------
# MCP TOOL — MCP client er UI thekeo AI ke ask kora jabe
# ------------------------------------------------------------

@mcp.tool()
def ask_assistant(
    question: str,
) -> dict[str, Any]:
    """
    Ask the AI assistant a natural-language question about your tasks.
    Examples:
      - "How many tasks do I have today?"
      - "What is the status of all tasks?"
      - "What is task 3 about?"
      - "How many pending tasks are left?"
    """
    try:
        answer = _answer_question(question)
        return {
            "success": True,
            "answer": answer,
        }
    except Exception as exc:
        return {
            "success": False,
            "message": f"{type(exc).__name__}: {exc}",
        }


# ------------------------------------------------------------
# TEXT CHAT MODE  →  python server_task_porosh.py --chat
# ------------------------------------------------------------

def run_chat_assistant() -> None:
    """Interactive text chat with the AI task assistant in the terminal."""

    try:
        _get_openai_client()
    except RuntimeError as exc:
        print(f"\n[ERROR] {exc}\n")
        return

    print()
    print("=" * 70)
    print("  TASK ASSISTANT — Text Chat (powered by OpenAI)")
    print("=" * 70)
    print("  Ask anything about your tasks in natural language.")
    print("  Examples:")
    print("    • How many tasks do I have today?")
    print("    • What tasks are completed?")
    print("    • What is the status of all my tasks?")
    print("    • How many pending tasks are left?")
    print()
    print("  Type 'exit' or 'quit' to leave the chat.")
    print("=" * 70)
    print()

    history: list[dict[str, str]] = []

    while True:

        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n[Chat closed]")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye", "q"}:
            print("\n[Chat closed]\n")
            break

        try:
            reply = _answer_question(user_input, history)
        except Exception as exc:
            print(f"\n[AI Error] {type(exc).__name__}: {exc}\n")
            continue

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})
        history[:] = history[-MAX_HISTORY_MESSAGES:]

        print(f"\nAssistant: {reply}\n")


# ------------------------------------------------------------
# VOICE CHAT MODE  →  python server_task_porosh.py --voice
# ------------------------------------------------------------

def run_voice_chat() -> None:
    """
    Voice mode: microphone e question bolen, AI-r uttor
    shonoa jabe (text-to-speech diye pora hoy).

    Requirements:
        pip install openai SpeechRecognition pyttsx3 pyaudio
    """

    # --- Check imports ---
    try:
        import speech_recognition as sr
        import pyttsx3
    except ImportError:
        print(
            "\n[ERROR] Voice packages are not installed.\n"
            "Run: pip install SpeechRecognition pyttsx3 pyaudio\n"
        )
        return

    # --- Check OpenAI ---
    try:
        _get_openai_client()
    except RuntimeError as exc:
        print(f"\n[ERROR] {exc}\n")
        return

    # --- Init speech engine ---
    recognizer = sr.Recognizer()

    try:
        engine = pyttsx3.init()
    except Exception as exc:
        print(f"\n[ERROR] Text-to-speech init failed: {exc}\n")
        return

    print()
    print("=" * 70)
    print("  TASK ASSISTANT — VOICE MODE (powered by OpenAI)")
    print("=" * 70)
    print("  Microphone e question bolen, AI uttor dibe.")
    print("  Examples:")
    print("    • How many tasks do I have today?")
    print("    • What tasks are completed?")
    print("    • What is the status of all my tasks?")
    print()
    print("  Voice chat bondho korte bolen: 'exit' / 'quit' / 'bye'")
    print("=" * 70)
    print()

    history: list[dict[str, str]] = []

    while True:

        # 1. Listen from microphone
        try:
            with sr.Microphone() as source:
                print("🎤 Listening... (speak now)")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source,
                    timeout=8,
                    phrase_time_limit=15,
                )
        except sr.WaitTimeoutError:
            print("[No speech detected — try again]\n")
            continue
        except Exception as exc:
            print(f"\n[ERROR] Microphone problem: {exc}\n"
                  "Check that a mic is connected and permitted.\n")
            return

        # 2. Speech -> Text
        try:
            question = recognizer.recognize_google(
                audio,
                language=VOICE_LANGUAGE,
            ).strip()
        except sr.UnknownValueError:
            print("[Could not understand — please repeat]\n")
            continue
        except sr.RequestError as exc:
            print(f"[Speech service error] {exc}\n")
            continue

        print(f"You (voice): {question}\n")

        if question.lower().rstrip(".!? ") in {"exit", "quit", "bye", "stop"}:
            print("[Voice chat closed]\n")
            break

        # 3. Ask OpenAI (live task snapshot shoho)
        try:
            reply = _answer_question(question, history)
        except Exception as exc:
            print(f"[AI Error] {type(exc).__name__}: {exc}\n")
            continue

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reply})
        history[:] = history[-MAX_HISTORY_MESSAGES:]

        # 4. Show + speak the reply
        print(f"Assistant: {reply}\n")
        engine.say(reply)
        engine.runAndWait()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    # Usage:
    #   python server_task_porosh.py            → MCP server mode (default)
    #   python server_task_porosh.py --chat     → terminal text chat
    #   python server_task_porosh.py --voice    → 🎤 voice chat

    if "--voice" in sys.argv:
        run_voice_chat()
    elif "--chat" in sys.argv:
        run_chat_assistant()
    else:
        mcp.run()
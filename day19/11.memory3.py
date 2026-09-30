import json
import os

from openai import OpenAI


openai_client = OpenAI()

MEMORY_FILE = "memory.json"


# --------------------------------
# Memory Store
# --------------------------------

def load_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(key: str, value: str) -> dict:
    memory = load_memory()

    memory[key] = value

    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)

    return {
        "status": "saved",
        "key": key,
        "value": value
    }


def retrieve_memory(query: str) -> dict:

    memory = load_memory()

    query_words = set(
        query.lower().split()
    )

    matches = []

    for key, value in memory.items():

        searchable_text = (
            f"{key} {value}"
        ).lower()

        searchable_words = set(
            searchable_text.split()
        )

        matching_words = query_words.intersection(
            searchable_words
        )

        if matching_words:
            matches.append(
                {
                    "key": key,
                    "value": value,
                    "matched_words": list(matching_words)
                }
            )

    return {
        "query": query,
        "matches": matches
    }


# --------------------------------
# Tool Definitions
# --------------------------------

available_tools = [
    {
        "type": "function",
        "name": "save_memory",
        "description": (
            "Save useful information about the user "
            "for future interactions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": (
                        "A descriptive key for the information."
                    )
                },
                "value": {
                    "type": "string",
                    "description": (
                        "The information to remember."
                    )
                }
            },
            "required": ["key", "value"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "retrieve_memory",
        "description": (
            "Search the user's stored memories using "
            "a natural-language query and return relevant memories."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A natural-language description of "
                        "the information being searched for."
                    )
                }
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    }
]


# --------------------------------
# Execute Memory Tool
# --------------------------------

def execute_memory_tool(
    tool_name: str,
    tool_arguments: dict
) -> dict:

    if tool_name == "save_memory":

        return save_memory(
            tool_arguments["key"],
            tool_arguments["value"]
        )

    if tool_name == "retrieve_memory":

        return retrieve_memory(
            tool_arguments["query"]
        )

    return {
        "error": f"Unknown tool: {tool_name}"
    }


# --------------------------------
# Process User Request
# --------------------------------

def process_user_request(user_request: str) -> None:

    model_input = [
        {
            "role": "developer",
            "content": """
You are a helpful personal assistant.

You have access to long-term user memory.

Use save_memory when the user tells you a useful
personal preference or fact that should be remembered
for future interactions.

Use retrieve_memory when the answer may depend on
something that was previously remembered.

When using retrieve_memory, provide a natural-language
query describing the information you need.

Do not claim to remember something unless the memory
tool actually returns relevant information.
"""
        },
        {
            "role": "user",
            "content": user_request
        }
    ]

    # --------------------------------
    # First LLM Call
    # --------------------------------

    llm_response = openai_client.responses.create(
        model="gpt-5.6",
        input=model_input,
        tools=available_tools
    )

    # --------------------------------
    # Handle Tool Call
    # --------------------------------

    for output_item in llm_response.output:

        if output_item.type == "function_call":

            tool_name = output_item.name

            tool_arguments = json.loads(
                output_item.arguments
            )

            print("\nAgent requested:")
            print(f"Tool: {tool_name}")
            print(f"Arguments: {tool_arguments}")

            tool_result = execute_memory_tool(
                tool_name,
                tool_arguments
            )

            print("\nTool result:")
            print(json.dumps(tool_result, indent=4))

            # --------------------------------
            # Send Tool Result Back to LLM
            # --------------------------------

            final_response = openai_client.responses.create(
                model="gpt-5.6",
                previous_response_id=llm_response.id,
                input=[
                    {
                        "type": "function_call_output",
                        "call_id": output_item.call_id,
                        "output": json.dumps(tool_result)
                    }
                ],
                tools=available_tools
            )

            print("\nAgent:")
            print(final_response.output_text)

            return

    # --------------------------------
    # No Tool Call
    # --------------------------------

    print("\nAgent:")
    print(llm_response.output_text)


# --------------------------------
# Main
# --------------------------------

def main() -> None:

    print("User: I prefer Dhaka for delivery.")

    process_user_request(
        "I prefer Dhaka for delivery."
    )

    print("\n================================")

    print("User: Where should you deliver my next order?")

    process_user_request(
        "Where should you deliver my next order?"
    )


if __name__ == "__main__":
    main()
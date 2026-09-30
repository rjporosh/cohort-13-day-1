import json
import os

from openai import OpenAI


openai_client = OpenAI()

MEMORY_FILE = "memory.json"


# --------------------------------
# Memory Functions
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


# --------------------------------
# Memory Tools
# --------------------------------

available_tools = [
    {
        "type": "function",
        "name": "save_memory",
        "description": "Save a useful piece of information about the user for future interactions.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The name of the information to remember."
                },
                "value": {
                    "type": "string",
                    "description": "The information to remember."
                }
            },
            "required": ["key", "value"],
            "additionalProperties": False
        },
        "strict": True
    }
]


# --------------------------------
# Process User Request
# --------------------------------

def process_user_request(user_request: str) -> None:

    memory = load_memory()

    memory_context = json.dumps(memory)

    model_input = [
        {
            "role": "developer",
            "content": (
                "You are a helpful personal assistant.\n\n"
                "The following information has been remembered "
                "about the user:\n"
                f"{memory_context}\n\n"
                "If the user tells you a useful personal preference "
                "or fact that should be remembered for future interactions, "
                "use the save_memory tool."
            )
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
    # Handle Tool Calls
    # --------------------------------

    for output_item in llm_response.output:

        if output_item.type == "function_call":

            tool_arguments = json.loads(
                output_item.arguments
            )

            tool_result = save_memory(
                tool_arguments["key"],
                tool_arguments["value"]
            )

            # --------------------------------
            # Send Memory Result Back to LLM
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

    print("\n--------------------------------")
    print("User: Where should you deliver my next order?")
    process_user_request(
        "Where should you deliver my next order?"
    )
if __name__ == "__main__":
    main()
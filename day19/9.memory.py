import json
import os
from openai import OpenAI

openai_client = OpenAI()
MEMORY_FILE = "memory.json"

# --------------------------------
# Memory
# --------------------------------
def load_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as file:
        return json.load(file)

def save_memory(memory: dict) -> None:
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)

# --------------------------------
# Process User Request
# --------------------------------
def process_user_request(user_request: str) -> None:
    memory = load_memory()
    # --------------------------------
    # First interaction:
    # Save user's preference
    # --------------------------------
    if "preferred delivery city" in user_request.lower():
        city = user_request.split("is")[-1].strip().rstrip(".")
        memory["preferred_delivery_city"] = city
        save_memory(memory)
        print("\nAgent:")
        print(f"Got it. I'll remember that your preferred delivery city is {city}.")

        return

    # --------------------------------
    # Later interaction:
    # Read Memory
    # --------------------------------
    memory_context = json.dumps(memory)
    model_input = [
        {
            "role": "developer",
            "content": (
                "The following information is stored in the user's memory:\n"
                f"{memory_context}\n\n"
                "Use this memory when it is relevant to the user's request."
            )
        },
        {
            "role": "user",
            "content": user_request
        }
    ]
    llm_response = openai_client.responses.create(
        model="gpt-5.6",
        input=model_input
    )
    print("\nAgent:")
    print(llm_response.output_text)

# --------------------------------
# Main
# --------------------------------
def main() -> None:
    print("User: My preferred delivery city is Dhaka.")
    process_user_request(
        "My preferred delivery city is Dhaka."
    )
    print("\n--------------------------------")
    print("User: Where should you deliver my next order?")
    process_user_request(
        "Where should you deliver my next order?"
    )

if __name__ == "__main__":
    main()
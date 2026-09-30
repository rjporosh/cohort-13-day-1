import json

from openai import OpenAI
openai_client = OpenAI()
# --------------------------------
# Structured Output Schema
# --------------------------------

decision_schema = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "order_status",
                "order_details",
                "cancel_order",
                "general_question"
            ]
        },
        "order_id": {
            "type": ["string", "null"]
        },
        "action": {
            "type": "string",
            "enum": [
                "get_order_status",
                "get_order_details",
                "cancel_order",
                "answer_directly"
            ]
        },
        "requires_tool": {
            "type": "boolean"
        }
    },
    "required": [
        "intent",
        "order_id",
        "action",
        "requires_tool"
    ],
    "additionalProperties": False
}


# --------------------------------
# Process User Request
# --------------------------------

def process_user_request(user_request: str) -> None:

    llm_response = openai_client.responses.create(
        model="gpt-5.6",
        instructions="""
You are an order support agent.

Analyze the user's request and determine:

1. The user's intent.
2. The order ID, if one is provided.
3. What action the application should take.
4. Whether a tool is required.

Return the decision using the provided structured schema.
""",
        input=user_request,
        text={
            "format": {
                "type": "json_schema",
                "name": "agent_decision",
                "strict": True,
                "schema": decision_schema
            }
        }
    )

    agent_decision = json.loads(
        llm_response.output_text
    )

    print("\nAgent Decision:")
    print(json.dumps(
        agent_decision,
        indent=4
    ))


# --------------------------------
# Main
# --------------------------------

def main() -> None:

    user_request = "Where is my order #1234?"

    process_user_request(user_request)

if __name__ == "__main__":
    main()
import json
from openai import OpenAI
openai_client = OpenAI()

# --------------------------------
# Tools
# --------------------------------
def get_order_status(order_id: str) -> dict:
    orders = {
        "1234": {
            "status": "Shipped",
            "location": "Dhaka",
            "expected_delivery": "September 26, 2026"
        },
        "5678": {
            "status": "Delivered",
            "location": "Chittagong",
            "expected_delivery": "September 28, 2026"
        }
    }

    return orders.get(
        order_id,
        {"status": "Order not found"}
    )

def get_order_details(order_id: str) -> dict:
    orders = {
        "1234": {
            "order_id": "1234",
            "product": "Laptop",
            "quantity": 1,
            "price": 85000,
            "status": "Shipped"
        },
        "5678": {
            "order_id": "5678",
            "product": "Smartphone",
            "quantity": 1,
            "price": 45000,
            "status": "Delivered"
        }
    }

    return orders.get(
        order_id,
        {"status": "Order not found"}
    )

def cancel_order(order_id: str) -> dict:
    orders = {
        "1234": {
            "status": "Cancellation requested"
        },
        "5678": {
            "status": "Cannot cancel",
            "reason": "Order has already been delivered"
        }
    }
    return orders.get(
        order_id,
        {"status": "Order not found"}
    )

# --------------------------------
# Describe Tools to the Model
# --------------------------------
available_tools = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Get the current status and delivery information of an order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The customer's order ID."
                }
            },
            "required": ["order_id"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_order_details",
        "description": "Get the detailed information of an order, including product, quantity, price, and status.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The customer's order ID."
                }
            },
            "required": ["order_id"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "cancel_order",
        "description": "Cancel a customer's order if cancellation is possible.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The customer's order ID."
                }
            },
            "required": ["order_id"],
            "additionalProperties": False
        },
        "strict": True
    }
]

# --------------------------------
# Tool Execution
# --------------------------------
def execute_tool(tool_name: str, tool_arguments: dict) -> dict:

    if tool_name == "get_order_status":
        return get_order_status(
            tool_arguments["order_id"]
        )

    if tool_name == "get_order_details":
        return get_order_details(
            tool_arguments["order_id"]
        )

    if tool_name == "cancel_order":
        return cancel_order(
            tool_arguments["order_id"]
        )

    return {
        "error": f"Unknown tool: {tool_name}"
    }

# --------------------------------
# Agent
# --------------------------------
def process_user_request(user_request: str) -> None:
    llm_response = openai_client.responses.create(
        model="gpt-5.6",
        input=user_request,
        tools=available_tools
    )

    for output_item in llm_response.output:
        if output_item.type == "function_call":
            print("Agent selected tool:")
            print(f"  Tool: {output_item.name}")
            print(f"  Arguments: {output_item.arguments}")
            tool_arguments = json.loads(
                output_item.arguments
            )

            tool_result = execute_tool(
                output_item.name,
                tool_arguments
            )
            print("\nTool result:")
            print(tool_result)

            final_response = openai_client.responses.create(
                model="gpt-5.6",
                input=[
                    {
                        "type": "function_call_output",
                        "call_id": output_item.call_id,
                        "output": json.dumps(tool_result)
                    }
                ],
                previous_response_id=llm_response.id
            )

            print("\nAgent response:")
            print(final_response.output_text)
            return
    print("Agent response:")
    print(llm_response.output_text)

# --------------------------------
# Application Entry Point
# --------------------------------
def main() -> None:

    #Try different requests
    #user_request = "Where is my order #1234?"
    #user_request = "Give me  the price and quantity of order #1234."
    #user_request = "I want to cancel order #1234."
    user_request = "What is the temperature of Dhaka right now?"
    print(user_request)
    process_user_request(user_request)

if __name__ == "__main__":
    main()
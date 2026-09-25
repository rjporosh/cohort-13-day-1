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
            "location": "Dhaka"
        },
        "5678": {
            "status": "Delivered",
            "location": "Chittagong"
        }
    }

    return orders.get(
        order_id,
        {"status": "Order not found"}
    )

def get_delivery_information(order_id: str) -> dict:
    deliveries = {
        "1234": {
            "expected_delivery": "September 22, 2026",
            "delivery_partner": "DHL"
        },
        "5678": {
            "delivered_on": "September 18, 2026",
            "delivery_partner": "FedEx"
        }
    }

    return deliveries.get(
        order_id,
        {"status": "Delivery information not found"}
    )

# --------------------------------
# Describe Tools to the Model
# --------------------------------
available_tools = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Get the current status and location of an order.",
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
        "name": "get_delivery_information",
        "description": "Get delivery information for an order, including expected delivery date and delivery partner.",
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
def execute_tool(
    tool_name: str,
    tool_arguments: dict
) -> dict:

    if tool_name == "get_order_status":
        return get_order_status(
            tool_arguments["order_id"]
        )

    if tool_name == "get_delivery_information":
        return get_delivery_information(
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
    while True:
        print("\nInside the while loop, processing LLM response...")
        tool_call_found = False
        for output_item in llm_response.output:
            if output_item.type != "function_call":
                continue
            tool_call_found = True
            print("\nAgent selected tool:")
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
            llm_response = openai_client.responses.create(
                model="gpt-5.6",
                input=[
                    {
                        "type": "function_call_output",
                        "call_id": output_item.call_id,
                        "output": json.dumps(tool_result)
                    }
                ],
                previous_response_id=llm_response.id,
                tools=available_tools
            )
            break

        if not tool_call_found:
            print("\nAgent response:")
            print(llm_response.output_text)
            break
# --------------------------------
# Application Entry Point
# --------------------------------
def main() -> None:
    user_request = (
        "Check order #1234. "
        "If it has been shipped, "
        "check its delivery information "
        "and tell me when I can expect it."
    )
    process_user_request(user_request)

if __name__ == "__main__":
    main()
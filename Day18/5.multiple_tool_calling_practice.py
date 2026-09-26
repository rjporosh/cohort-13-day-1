import json
import os
from openai import OpenAI

client = OpenAI()

# --------------------------------
# Data File
# --------------------------------

DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data.json"
)


# --------------------------------
# Data Access
# --------------------------------

def load_data():

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# --------------------------------
# Tools
# --------------------------------

def get_customer_info(customer_id: str) -> dict:

    data = load_data()

    customer = data["customers"].get(customer_id)

    if not customer:
        return {
            "status": "Customer not found"
        }

    return {
        "customer_id": customer_id,
        **customer
    }


def get_order_info(order_id: str) -> dict:

    data = load_data()

    order = data["orders"].get(order_id)

    if not order:
        return {
            "status": "Order not found"
        }

    return {
        "order_id": order_id,
        **order
    }


def create_support_request(
    customer_id: str,
    order_id: str,
    issue: str
) -> dict:

    data = load_data()

    if customer_id not in data["customers"]:
        return {
            "status": "Customer not found"
        }

    if order_id not in data["orders"]:
        return {
            "status": "Order not found"
        }

    request_id = str(
        len(data["support_requests"]) + 1
    )

    request = {
        "request_id": request_id,
        "customer_id": customer_id,
        "order_id": order_id,
        "issue": issue,
        "status": "Open"
    }

    data["support_requests"].append(request)

    save_data(data)

    return {
        "status": "Support request created",
        "request": request
    }


def get_support_requests(customer_id: str) -> dict:

    data = load_data()

    requests = [
        request
        for request in data["support_requests"]
        if request["customer_id"] == customer_id
    ]

    return {
        "customer_id": customer_id,
        "requests": requests
    }


# --------------------------------
# Tool Definitions
# --------------------------------

available_tools = [

    {
        "type": "function",
        "name": "get_customer_info",
        "description": "Get customer information using customer ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer's ID."
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_order_info",
        "description": "Get order information using order ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID."
                }
            },
            "required": ["order_id"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "create_support_request",
        "description": "Create a new support request for a customer and save it to the data file.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer's ID."
                },
                "order_id": {
                    "type": "string",
                    "description": "The order ID related to the support request."
                },
                "issue": {
                    "type": "string",
                    "description": "The customer's problem or support request."
                }
            },
            "required": [
                "customer_id",
                "order_id",
                "issue"
            ],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_support_requests",
        "description": "Get previous support requests of a customer.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer's ID."
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False
        },
        "strict": True
    }
]


# --------------------------------
# Tool Execution
# --------------------------------

def execute_tool(tool_name, tool_arguments):

    if tool_name == "get_customer_info":

        return get_customer_info(
            tool_arguments["customer_id"]
        )

    if tool_name == "get_order_info":

        return get_order_info(
            tool_arguments["order_id"]
        )

    if tool_name == "create_support_request":

        return create_support_request(
            tool_arguments["customer_id"],
            tool_arguments["order_id"],
            tool_arguments["issue"]
        )

    if tool_name == "get_support_requests":

        return get_support_requests(
            tool_arguments["customer_id"]
        )

    return {
        "error": f"Unknown tool: {tool_name}"
    }


# --------------------------------
# Agent
# --------------------------------

def process_user_request(user_request):

    response = client.responses.create(
        model="gpt-5.6",
        input=user_request,
        tools=available_tools
    )

    # Keep calling tools until the agent finishes
    while True:

        tool_outputs = []

        for output_item in response.output:

            if output_item.type == "function_call":

                print("\nAgent selected tool:")
                print(f"Tool: {output_item.name}")
                print(f"Arguments: {output_item.arguments}")

                tool_arguments = json.loads(
                    output_item.arguments
                )

                tool_result = execute_tool(
                    output_item.name,
                    tool_arguments
                )

                print("\nTool result:")
                print(tool_result)

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": output_item.call_id,
                    "output": json.dumps(
                        tool_result,
                        ensure_ascii=False
                    )
                })

        # No more tool calls
        if not tool_outputs:

            print("\nAgent response:")
            print(response.output_text)

            return

        # Send tool result back to the agent
        response = client.responses.create(
            model="gpt-5.6",
            input=tool_outputs,
            previous_response_id=response.id
        )


# --------------------------------
# Application Entry Point
# --------------------------------

def main():

    user_request = input(
        "Enter your request: "
    )

    process_user_request(user_request)


if __name__ == "__main__":
    main()

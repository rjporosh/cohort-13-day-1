import json
from openai import OpenAI

client = OpenAI()


# ============================================================
# DATA
# ============================================================

customers = {
    "101": {
        "name": "Md. Ikramul Islam Siddique Porosh",
        "email": "porosh@example.com",
        "phone": "01672896992"
    },
    "102": {
        "name": "Karim Hasan",
        "email": "karim@example.com",
        "phone": "01822222222"
    }
}


orders = {
    "1234": {
        "order_id": "1234",
        "customer_id": "101",
        "product": "Laptop",
        "price": 85000,
        "status": "Shipped"
    },

    "1212": {
        "order_id": "1212",
        "customer_id": "101",
        "product": "Smartphone",
        "price": 45000,
        "status": "Processing"
    }
}


support_requests = [
    {
        "customer_id": "101",
        "order_id": "1001",
        "issue": "Product arrived damaged"
    }
]


# ============================================================
# TOOLS
# ============================================================

def get_customer(customer_id):
    return customers.get(
        customer_id,
        {"error": "Customer not found"}
    )


def get_order(order_id):
    return orders.get(
        order_id,
        {"error": "Order not found"}
    )


def create_support_request(customer_id, order_id, issue):

    request = {
        "customer_id": customer_id,
        "order_id": order_id,
        "issue": issue
    }

    support_requests.append(request)

    return {
        "success": True,
        "message": "Support request created successfully",
        "request": request
    }


def get_previous_requests(customer_id):

    requests = [
        request
        for request in support_requests
        if request["customer_id"] == customer_id
    ]

    return {
        "customer_id": customer_id,
        "requests": requests
    }


# ============================================================
# TOOL DEFINITIONS
# ============================================================

tools = [

    {
        "type": "function",
        "name": "get_customer",
        "description": "Get customer name, email and basic information using customer ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string"
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_order",
        "description": "Get order information including customer, product, price and status.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string"
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
        "description": "Create and save a customer's support request.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string"
                },
                "order_id": {
                    "type": "string"
                },
                "issue": {
                    "type": "string"
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
        "name": "get_previous_requests",
        "description": "Get all previous support requests of a customer.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string"
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False
        },
        "strict": True
    }
]


# ============================================================
# TOOL EXECUTOR
# ============================================================

def execute_tool(name, arguments):

    if name == "get_customer":
        return get_customer(
            arguments["customer_id"]
        )

    if name == "get_order":
        return get_order(
            arguments["order_id"]
        )

    if name == "create_support_request":
        return create_support_request(
            arguments["customer_id"],
            arguments["order_id"],
            arguments["issue"]
        )

    if name == "get_previous_requests":
        return get_previous_requests(
            arguments["customer_id"]
        )

    return {
        "error": f"Unknown tool: {name}"
    }


# ============================================================
# AGENT
# ============================================================

def run_agent(user_message, previous_response_id=None):

    response = client.responses.create(
        model="gpt-5.6",
        input=user_message,
        tools=tools,
        previous_response_id=previous_response_id
    )

    # Keep working until the agent has no more tools to call
    while True:

        tool_outputs = []

        for item in response.output:

            if item.type == "function_call":

                print("\n🔧 Agent is using:", item.name)

                arguments = json.loads(item.arguments)

                print("   Arguments:", arguments)

                result = execute_tool(
                    item.name,
                    arguments
                )

                print("   Result:", result)

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result)
                })

        # No tool call = agent has finished
        if not tool_outputs:
            print("\n🤖 Agent:")
            print(response.output_text)

            return response.id

        # Send ALL tool results back to the model
        response = client.responses.create(
            model="gpt-5.6",
            previous_response_id=response.id,
            input=tool_outputs
        )


# ============================================================
# CHAT
# ============================================================

def main():

    print("Customer Support Agent")
    print("Type 'exit' to stop.\n")

    previous_response_id = None

    while True:

        user_message = input("You: ")

        if user_message.lower() == "exit":
            break

        previous_response_id = run_agent(
            user_message,
            previous_response_id
        )


if __name__ == "__main__":
    main()
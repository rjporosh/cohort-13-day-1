import json
from pathlib import Path
from openai import OpenAI

client = OpenAI()

# ============================================================
# DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# data.json is the seed/master data file.
# If this script is inside Day18/, data.json is in the parent folder.
DATA_FILE = BASE_DIR.parent / "data.json"


def load_data():
    """Load seed/master data from data.json."""
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_complaint_file(customer_id):
    """Return the complaint file path for a customer."""
    return BASE_DIR.parent / f"customer-{customer_id}-complaint.json"


def load_complaints(customer_id):
    """
    Load a customer's complaints.

    If the customer's complaint file does not exist yet,
    initialize it with that customer's seed complaints from data.json.
    """
    complaint_file = get_complaint_file(customer_id)

    if complaint_file.exists():
        with complaint_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    data = load_data()

    complaints = [
        request
        for request in data.get("support_requests", [])
        if request["customer_id"] == customer_id
    ]

    with complaint_file.open("w", encoding="utf-8") as file:
        json.dump(complaints, file, indent=4, ensure_ascii=False)

    return complaints


def save_complaints(customer_id, complaints):
    """Save all complaints for a customer without deleting previous ones."""
    complaint_file = get_complaint_file(customer_id)

    with complaint_file.open("w", encoding="utf-8") as file:
        json.dump(complaints, file, indent=4, ensure_ascii=False)


# ============================================================
# TOOLS
# ============================================================

def get_customer(customer_id):
    data = load_data()

    return data["customers"].get(
        customer_id,
        {"error": "Customer not found"}
    )


def get_order(order_id):
    data = load_data()

    return data["orders"].get(
        order_id,
        {"error": "Order not found"}
    )


def create_support_request(customer_id, order_id, issue):
    data = load_data()

    if customer_id not in data["customers"]:
        return {"error": "Customer not found"}

    if order_id not in data["orders"]:
        return {"error": "Order not found"}

    # Read existing complaints first.
    # This preserves every previous complaint.
    complaints = load_complaints(customer_id)

    request = {
        "customer_id": customer_id,
        "order_id": order_id,
        "issue": issue
    }

    # Only append the new complaint.
    complaints.append(request)

    # Save the complete list back to the customer's file.
    save_complaints(customer_id, complaints)

    return {
        "success": True,
        "message": "Support request created successfully",
        "request": request
    }


def get_previous_requests(customer_id):
    data = load_data()

    if customer_id not in data["customers"]:
        return {"error": "Customer not found"}

    # Previous complaints come from the customer's own file.
    complaints = load_complaints(customer_id)

    return {
        "customer_id": customer_id,
        "requests": complaints
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
        "description": "Create a new support request and append it to the customer's complaint file without deleting previous complaints.",
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
        "description": "Get all previous support requests of a customer from that customer's complaint file.",
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

    # Keep working until the agent has no more tools to call.
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
                    "output": json.dumps(
                        result,
                        ensure_ascii=False
                    )
                })

        # No tool call = agent has finished.
        if not tool_outputs:
            print("\n🤖 Agent:")
            print(response.output_text)

            return response.id

        # Send all tool results back to the model.
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

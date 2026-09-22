import json


from openai import OpenAI
openai_client = OpenAI()


# --------------------------------
# Tool
# --------------------------------
def get_order_status(order_id: str) -> dict:
    orders = {
        "1234": {
            "status": "Shipped",
            "location": "Dhaka",
            "expected_delivery": "September 22, 2026"
        },
        "5678": {
            "status": "Delivered",
            "location": "Chittagong",
            "expected_delivery": "September 18, 2026"
        }
    }
    return orders.get(
        order_id,
        {"status": "Order not found"}
    )


# --------------------------------
# Agent
# --------------------------------


def process_user_request(user_request: str) -> None:


    llm_response = openai_client.responses.create(
        model="gpt-5.6",
        input=f"""
        You are an order support agent.


        User request:
        {user_request}


        If the user is asking about an order status,
        you should use the get_order_status tool.


        Otherwise, answer the user directly.
        """
    )


    agent_reply = llm_response.output_text


    print("Agent:")
    print(agent_reply)




# --------------------------------
# Application Entry Point
# --------------------------------


def main() -> None:
    user_request = "Where is my order #1234?"
    process_user_request(user_request)




if __name__ == "__main__":
    main()

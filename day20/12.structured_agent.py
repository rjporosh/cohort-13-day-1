from openai import OpenAI

openai_client = OpenAI()
def process_user_request(user_request: str) -> None:
    llm_response = openai_client.responses.create(
        model="gpt-5.6",
        instructions="""
You are an order support agent.

Analyze the user's request and return a structured
decision.

Determine:

1. intent
2. order_id
3. action
4. requires_tool

Possible intents:
- order_status
- order_details
- cancel_order
- general_question

Possible actions:
- get_order_status
- get_order_details
- cancel_order
- answer_directly

Return only the structured result.
""",
        input=user_request
    )
    print("Agent Decision:")
    print(llm_response.output_text)

def main() -> None:
    user_request = "Where is my order #1234?"
    process_user_request(user_request)

if __name__ == "__main__":
    main()
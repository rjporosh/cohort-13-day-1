from openai import OpenAI
openai_client = OpenAI()


def main() -> None:
    user_request = "Share me the latest news about AI advancements in the world."
    llm_response = openai_client.responses.create(
        model="gpt-5.6",
        input=user_request
    )
    print(llm_response.output_text)


if __name__ == "__main__":
    main()

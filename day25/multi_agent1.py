from openai import OpenAI
client = OpenAI()

# ============================================
# Specialist Agent
# ============================================

def writing_agent(task: str) -> str:
    """
    Specialist Agent responsible for writing tasks.
    """
    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions="""
        You are a Writing Specialist Agent.
        Your job is to help with writing tasks,
        including rewriting, improving clarity,
        and correcting grammar.
        Complete the assigned task directly.
        """,
        input=task
    )
    return response.output_text

# ============================================
# Supervisor Agent
# ============================================
def supervisor_agent(user_request: str) -> str:
    """
    Supervisor decides whether to delegate
    the request to the Writing Agent.
    """
    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions="""
        You are a Supervisor Agent.
        You coordinate the work of specialist agents.
        There is one available specialist:
        1. writing_agent:
           Handles rewriting, grammar correction,
           and improving written content.

        If the user request is a writing task,
        return exactly:

        DELEGATE: <the task to assign>
        Otherwise, respond directly to the user.
        Do not execute the writing task yourself
        when delegation is appropriate.
        """,
        input=user_request
    )
    decision = response.output_text.strip()
    print("\n--- SUPERVISOR DECISION ---")
    print(decision)
    # Delegate the task to the Specialist Agent.
    if decision.startswith("DELEGATE:"):
        specialist_task = decision[len("DELEGATE:"):].strip()
        print("\n--- SPECIALIST TASK ---")
        print(specialist_task)
        specialist_result = writing_agent(specialist_task)
        print("\n--- SPECIALIST RESULT ---")
        print(specialist_result)
        return specialist_result
    return decision

# ============================================
# Main
# ============================================
def main():
    user_request = input("What would you like help with? ")
    result = supervisor_agent(user_request)
    print("\n--- FINAL RESPONSE ---")
    print(result)

if __name__ == "__main__":
    main()
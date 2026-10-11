import json
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5.6-luna"

def writing_agent(task: str) -> str:
    """
    Specialist Agent for writing-related tasks.
    """
    response = client.responses.create(
        model=MODEL,
        instructions="""
        You are a Writing Specialist Agent.
        Your responsibilities include:
        - Rewriting text
        - Improving clarity
        - Correcting grammar
        - Improving professional communication
        Complete the assigned task directly.
        Return only the result.
        """,
        input=task
    )

    return response.output_text

def coding_agent(task: str) -> str:
    """
    Specialist Agent for programming-related tasks.
    """
    response = client.responses.create(
        model=MODEL,
        instructions="""
        You are a Coding Specialist Agent.
        Your responsibilities include:
        - Answering programming questions
        - Explaining code
        - Identifying programming errors
        - Suggesting code improvements
        Provide technically accurate and clear answers.
        Include code examples when useful.
        """,
        input=task
    )
    return response.output_text

def analysis_agent(task: str) -> str:
    """
    Specialist Agent for analytical tasks.
    """
    response = client.responses.create(
        model=MODEL,
        instructions="""
        You are an Analysis Specialist Agent.
        Your responsibilities include:
        - Analyzing information
        - Identifying patterns
        - Comparing alternatives
        - Explaining findings
        - Providing evidence-based recommendations
        Do not invent data that was not provided.
        Clearly identify assumptions when necessary.
        """,
        input=task
    )
    return response.output_text

available_agents = {
    "writing_agent": writing_agent,
    "coding_agent": coding_agent,
    "analysis_agent": analysis_agent
}

agents = available_agents

def supervisor_agent(user_request: str) -> dict:
    """
    Understand the user's request and select
    the most appropriate Specialist Agent.
    """
    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "developer",
                "content": """
                You are a Supervisor Agent.

                Your responsibility is to route user requests
                to the most appropriate Specialist Agent.

                Available agents:

                1. writing_agent
                   For rewriting, grammar correction,
                   professional communication and writing.

                2. coding_agent
                   For programming, debugging,
                   code explanations and technical coding tasks.

                3. analysis_agent
                   For analyzing information, comparing options,
                   identifying patterns and recommendations.

                4. none
                   Use this when the request does not fit
                   any of the available specialist agents.

                Select exactly one agent.

                The task field must contain the task that
                should be assigned to the selected agent.

                Do not perform the specialist's task yourself.
                Return only the structured decision.
                """
            },
            {
                "role": "user",
                "content": user_request
            }
        ],

        text={
            "format": {
                "type": "json_schema",
                "name": "supervisor_decision",
                "strict": True,

                "schema": {
                    "type": "object",

                    "properties": {
                        "agent": {
                            "type": "string",
                            "enum": [
                                "writing_agent",
                                "coding_agent",
                                "analysis_agent",
                                "none"
                            ]
                        },

                        "reason": {
                            "type": "string"
                        },

                        "task": {
                            "type": "string"
                        }
                    },

                    "required": [
                        "agent",
                        "reason",
                        "task"
                    ],

                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.output_text)

# ============================================
# AGENT ORCHESTRATION
# ============================================
def run_multi_agent_system(user_request: str) -> str:
    """
    Coordinates the Supervisor and Specialist Agents.
    """
    # ----------------------------------------
    # Step 1: Supervisor makes a decision
    # ----------------------------------------
    decision = supervisor_agent(user_request)

    print("\n--- SUPERVISOR DECISION ---")

    print(
        json.dumps(
            decision,
            indent=4
        )
    )

    agent_name = decision["agent"]
    task = decision["task"]

    # ----------------------------------------
    # Step 2: Validate the decision
    # ----------------------------------------

    if agent_name == "none":
        return (
            "I couldn't identify an appropriate specialist "
            "for this request."
        )

    if agent_name not in agents:
        return "The selected agent is not available."

    if not task.strip():
        return "The Supervisor did not provide a task."

    # ----------------------------------------
    # Step 3: Select the Specialist Agent
    # ----------------------------------------

    specialist = agents[agent_name]
    print(f"\nSelected Agent: {agent_name}")

    # ----------------------------------------
    # Step 4: Execute the Specialist Agent
    # ----------------------------------------
    specialist_result = specialist(task)

    print("\n--- SPECIALIST RESULT ---")
    print(specialist_result)

    return specialist_result

# ============================================
# MAIN
# ============================================

def main():
    print("=== Multi-Agent System: Version 2 ===")
    user_request = input(
        "\nWhat would you like help with? "
    )
    result = run_multi_agent_system(user_request)
    print("\n--- FINAL RESPONSE ---")
    print(result)

if __name__ == "__main__":
    main()
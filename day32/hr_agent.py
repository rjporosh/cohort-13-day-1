
import json
import ollama


# ==========================================
# 1. EMPLOYEE DATABASE
# ==========================================

employees = {
    101: {
        "name": "Rahim",
        "position": "Software Engineer",
        "next_position": "Senior Software Engineer",
        "increment": 15
    },
    102: {
        "name": "Karim",
        "position": "HR Executive",
        "next_position": "HR Manager",
        "increment": 12
    },
    103: {
        "name": "Hasan",
        "position": "Junior Accountant",
        "next_position": "Senior Accountant",
        "increment": 10
    }
}


# ==========================================
# 2. AGENT TOOL
# ==========================================

def get_employee_career_info(employee_id, topic):

    employee = employees.get(employee_id)

    if not employee:
        return f"Employee ID {employee_id} was not found."

    if topic == "position":
        return (
            f"Employee ID: {employee_id}\n"
            f"Name: {employee['name']}\n"
            f"Current Position: {employee['position']}\n"
            f"Next Position: {employee['next_position']}"
        )

    if topic == "salary":
        return (
            f"Employee ID: {employee_id}\n"
            f"Expected Salary Increment: {employee['increment']}%"
        )

    if topic == "both":
        return (
            f"Employee ID: {employee_id}\n"
            f"Current Position: {employee['position']}\n"
            f"Next Position: {employee['next_position']}\n"
            f"Expected Salary Increment: {employee['increment']}%"
        )


# ==========================================
# 3. LLM INTENT SCHEMA
# ==========================================

intent_schema = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": [
                "position",
                "salary",
                "both",
                "out_of_scope",
                "need_id",
                "unclear"
            ]
        },
        "employee_id": {
            "type": ["integer", "null"]
        }
    },
    "required": ["action", "employee_id"]
}


# ==========================================
# 4. AGENT INSTRUCTIONS
# ==========================================

SYSTEM_PROMPT = """
You are an intelligent HR Career Assistant.

Your responsibilities are limited to:
1. Employee next job position.
2. Employee expected salary increment percentage.

Understand both English and Bengali naturally.

Identify the user's intent and return structured JSON only.

Rules:
- position: User asks about promotion or next job position.
- salary: User asks about salary or increment percentage.
- both: User asks about both.
- out_of_scope: Any unrelated question.
- need_id: HR-related question but no employee ID is available.
- unclear: The request is ambiguous.

Extract the employee ID if mentioned.
If the user refers to a previously mentioned employee,
use that employee's ID.

Never invent employee data.
Never answer unrelated questions.
"""


# ==========================================
# 5. HR CAREER AGENT
# ==========================================

def hr_career_agent(user_question, current_employee_id=None):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Previously identified Employee ID: "
                f"{current_employee_id}\n"
                f"User question: {user_question}"
            )
        }
    ]

    # LLM understands the question and identifies intent
    response = ollama.chat(
        model="qwen2.5:3b",
        messages=messages,
        format=intent_schema,
        options={"temperature": 0}
    )

    result = json.loads(response.message.content)

    action = result["action"]
    employee_id = result["employee_id"] or current_employee_id

    # Handle unsupported questions
    if action == "out_of_scope":
        return (
            current_employee_id,
            "দুঃখিত! আমি শুধু Salary এবং Job Position "
            "সংক্রান্ত প্রশ্নের উত্তর দিতে পারি।"
        )

    # Handle missing Employee ID
    if action == "need_id" or employee_id is None:
        return (
            current_employee_id,
            "অনুগ্রহ করে আপনার Employee ID প্রদান করুন।"
        )

    # Handle unclear questions
    if action == "unclear":
        return (
            employee_id,
            "আপনি কি আপনার Salary Increment "
            "নাকি Next Job Position জানতে চান?"
        )

    # Agent decides which tool to execute
    tool_result = get_employee_career_info(
        employee_id,
        action
    )

    # Validate Employee ID
    if "was not found" in tool_result:
        return None, "দুঃখিত! Employee ID পাওয়া যায়নি।"

    # LLM selected the tool; Python returns trusted data
    return employee_id, tool_result


# ==========================================
# 6. CONVERSATIONAL INTERFACE
# ==========================================

def main():

    current_employee_id = None

    print("=" * 45)
    print("       HR CAREER ASSISTANT AGENT")
    print("=" * 45)
    print("Ask me about your Salary or Job Position.")
    print("Type 'exit' to stop.\n")

    while True:

        user_question = input("You: ").strip()

        if user_question.lower() == "exit":
            print("Agent: Thank you! Goodbye.")
            break

        if not user_question:
            continue

        try:
            current_employee_id, answer = hr_career_agent(
                user_question,
                current_employee_id
            )

            print(f"\nAgent: {answer}\n")

        except Exception as error:
            print(f"\nAgent Error: {error}\n")


if __name__ == "__main__":
    main()

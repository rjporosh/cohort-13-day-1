
import json
import ollama


# ==========================================
# 1. EMPLOYEE DATA
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
# 2. POSITION TOOL
# ==========================================

def get_next_position(employee_id):

    employee = employees.get(employee_id)

    if not employee:
        return None

    return (
        f"আপনার Employee ID: {employee_id}\n\n"
        f"আপনার বর্তমান পদ {employee['position']}।\n\n"
        f"আপনার সম্ভাব্য পরবর্তী পদ "
        f"{employee['next_position']}।"
    )


# ==========================================
# 3. SALARY TOOL
# ==========================================

def get_salary_increment(employee_id):

    employee = employees.get(employee_id)

    if not employee:
        return None

    return (
        f"আপনার Employee ID: {employee_id}\n\n"
        f"আপনার সম্ভাব্য salary increment প্রায় "
        f"{employee['increment']}%।"
    )


# ==========================================
# 4. LLM CONFIGURATION
# ==========================================

SYSTEM_PROMPT = """
You are an HR Career Assistant.

Your responsibilities are ONLY:

1. Employee next job position.
2. Employee expected salary increment percentage.

Understand Bengali and English naturally.

Identify the user's intent and employee ID.

Return structured JSON with these fields:

action: one of
- position
- salary
- both
- out_of_scope
- need_id
- unclear

employee_id: integer or null

Rules:
- position: Questions about next job position.
- salary: Questions about salary increment.
- both: Questions about both.
- out_of_scope: Unrelated questions.
- need_id: HR questions without an available employee ID.
- unclear: Ambiguous questions.

Use the previous employee ID if the user refers
to the same employee without mentioning the ID again.

Never invent employee information.
Never answer questions outside your responsibilities.
"""


INTENT_SCHEMA = {
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
# 5. HR CAREER AGENT
# ==========================================

def hr_career_agent(question, previous_id=None):

    response = ollama.chat(
        model="qwen2.5-coder:14b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"Previous Employee ID: {previous_id}\n"
                    f"Current Question: {question}"
                )
            }
        ],
        format=INTENT_SCHEMA,
        options={"temperature": 0}
    )

    intent = json.loads(response.message.content)

    action = intent["action"]
    employee_id = intent["employee_id"]

    if action == "out_of_scope":

        return previous_id, (
            "দুঃখিত! আমি শুধু আপনার Salary এবং "
            "Job Position সংক্রান্ত প্রশ্নের উত্তর দিতে পারি। "
            "এ ধরনের প্রশ্নের বাইরে উত্তর দিতে আমি অপরাগ।"
        )

    # Use previous ID when current ID is unavailable
    if employee_id is None:
        employee_id = previous_id

    if action == "need_id" or employee_id is None:

        return previous_id, (
            "অনুগ্রহ করে আপনার Employee ID প্রদান করুন।"
        )

    if action == "unclear":

        return employee_id, (
            "আপনি কি আপনার Salary Increment "
            "নাকি Next Job Position জানতে চান?"
        )

    # Validate Employee ID
    if employee_id not in employees:

        return None, (
            "দুঃখিত! আপনার Employee ID পাওয়া যায়নি।"
        )

    # Execute the appropriate tools
    if action == "position":

        answer = get_next_position(employee_id)

    elif action == "salary":

        answer = get_salary_increment(employee_id)

    elif action == "both":

        answer = (
            get_next_position(employee_id)
            + "\n\n"
            + get_salary_increment(employee_id).split("\n\n", 1)[1]
        )

    else:

        answer = (
            "দুঃখিত! আপনার প্রশ্নটি বুঝতে পারিনি। "
            "আবার চেষ্টা করুন।"
        )

    return employee_id, answer


# ==========================================
# 6. MAIN CONVERSATION LOOP
# ==========================================

def main():

    previous_id = None

    print("=" * 45)
    print("       HR CAREER ASSISTANT AGENT")
    print("=" * 45)

    print("Ask about Salary or Job Position.")
    print("Type 'exit' to stop.\n")

    while True:

        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Agent: Thank you! Goodbye.")
            break

        if not question:
            continue

        try:

            previous_id, answer = hr_career_agent(
                question,
                previous_id
            )

            print(f"\nAgent:\n{answer}\n")

        except Exception as error:

            print(f"\nAgent Error: {error}\n")


if __name__ == "__main__":
    main()

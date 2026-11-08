
# HR Career Assistant Agent

# 1. Sample Employee Data
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


# 2. HR Career Assistant Agent
def hr_career_agent(employee_id, question):

    # Check Employee ID
    employee = employees.get(employee_id)

    if not employee:
        return "দুঃখিত! আপনার Employee ID পাওয়া যায়নি।"

    # Check question category
    question = question.lower()

    # Next Job Position
    if any(word in question for word in ["position", "পদ", "পজিশন", "promotion"]):
        return (
            f"আপনার Employee ID: {employee_id}\n"
            f"আপনার বর্তমান পদ {employee['position']}।\n"
            f"আপনার সম্ভাব্য পরবর্তী পদ {employee['next_position']}।"
        )

    # Salary Increment
    elif any(word in question for word in ["salary", "increment", "বেতন", "বাড়তে", "%"]):
        return (
            f"আপনার Employee ID: {employee_id}\n"
            f"আপনার সম্ভাব্য salary increment প্রায় "
            f"{employee['increment']}%।"
        )

    # Unsupported Questions
    else:
        return (
            "দুঃখিত! আমি শুধু আপনার Salary এবং Job Position "
            "সংক্রান্ত প্রশ্নের উত্তর দিতে পারি। "
            "এ ধরনের প্রশ্নের বাইরে উত্তর দিতে আমি অপরাগ।"
        )


# 3. Agent Interaction
print("Welcome to HR Career Assistant!")
print("Type 'exit' to stop the agent.")

while True:

    user_input = input("\nআপনার প্রশ্ন লিখুন: ").strip()

    if user_input.lower() == "exit":
        print("ধন্যবাদ! HR Career Assistant ব্যবহার করার জন্য।")
        break

    try:
        employee_id = int(input("আপনার Employee ID লিখুন: "))

        response = hr_career_agent(employee_id, user_input)

        print("\nAGENT:")
        print(response)

    except ValueError:
        print("দুঃখিত! Employee ID অবশ্যই সংখ্যায় লিখতে হবে।")

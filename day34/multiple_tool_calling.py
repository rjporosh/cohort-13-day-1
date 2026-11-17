import json
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5.6"

# -------------------------------------------------------------------
# Mock HR data. In a real application, these methods would query
# authenticated HR databases or internal APIs.
# -------------------------------------------------------------------

EMPLOYEES = {
    "E001": {
        "employee_id": "E001",
        "name": "John Doe",
        "designation": "Senior Software Engineer",
        "department_id": "D001",
        "joining_date": "2021-04-12",
        "manager_id": "M001",
    },
    "E002": {
        "employee_id": "E002",
        "name": "Jane Smith",
        "designation": "Software Engineer",
        "department_id": "D001",
        "joining_date": "2022-03-15",
        "manager_id": "M001",
    },
}

SALARIES = {
    "E001": {"monthly_salary": 90000, "currency": "BDT", "payment_date": "2026-11-01"},
    "E002": {"monthly_salary": 75000, "currency": "BDT", "payment_date": "2026-11-01"},
}

LEAVE_BALANCES = {
    "E001": {"annual_leave": 15, "sick_leave": 8, "casual_leave": 4},
    "E002": {"annual_leave": 12, "sick_leave": 8, "casual_leave": 5},
}

ATTENDANCE = {
    "E001": {"month": "2026-11", "present_days": 18, "absent_days": 0, "late_days": 1},
    "E002": {"month": "2026-11", "present_days": 17, "absent_days": 1, "late_days": 2},
}

DEPARTMENTS = {
    "D001": {
        "department_id": "D001",
        "name": "Engineering",
        "head": "Mr. Rahman",
        "location": "Dhaka",
    },
}

MANAGERS = {
    "M001": {
        "manager_id": "M001",
        "name": "Mr. Rahman",
        "designation": "Engineering Manager",
        "email": "rahman@example.com",
    },
}

COMPANY_HOLIDAYS = [
    {"date": "2026-12-16", "name": "Victory Day"},
    {"date": "2026-12-25", "name": "Christmas Day"},
]

JOB_OPENINGS = [
    {"title": "Backend Engineer", "department": "Engineering", "location": "Dhaka"},
    {"title": "Product Designer", "department": "Product", "location": "Dhaka"},
]

TRAINING_COURSES = [
    {"title": "Secure Coding Fundamentals", "provider": "Learning & Development"},
    {"title": "Leadership Essentials", "provider": "Learning & Development"},
]

PAYROLL_STATUS = {
    "E001": {"month": "2026-11", "status": "Processed", "payment_date": "2026-11-01"},
    "E002": {"month": "2026-11", "status": "Processed", "payment_date": "2026-11-01"},
}


# -------------------------------------------------------------------
# 10 Python tools: deterministic business/data-access functions
# -------------------------------------------------------------------

def get_employee_info(employee_id: str) -> dict:
    """Return the employee's basic profile."""
    employee = EMPLOYEES.get(employee_id)
    if not employee:
        return {"status": "Employee not found", "employee_id": employee_id}
    return employee

def get_salary_info(employee_id: str) -> dict:
    """Return current salary information for an employee."""
    salary = SALARIES.get(employee_id)
    if not salary:
        return {"status": "Salary information not found", "employee_id": employee_id}
    return {"employee_id": employee_id, **salary}

def get_leave_balance(employee_id: str) -> dict:
    """Return remaining annual, sick, and casual leave balances."""
    balance = LEAVE_BALANCES.get(employee_id)
    if not balance:
        return {"status": "Leave balance not found", "employee_id": employee_id}
    return {"employee_id": employee_id, **balance}

def get_attendance_info(employee_id: str) -> dict:
    """Return attendance information for the current mock reporting month."""
    attendance = ATTENDANCE.get(employee_id)
    if not attendance:
        return {"status": "Attendance information not found", "employee_id": employee_id}
    return {"employee_id": employee_id, **attendance}

def get_department_info(department_id: str) -> dict:
    """Return information about a department."""
    department = DEPARTMENTS.get(department_id)
    if not department:
        return {"status": "Department not found", "department_id": department_id}
    return department

def get_company_holidays() -> dict:
    """Return the list of upcoming company holidays."""
    return {"holidays": COMPANY_HOLIDAYS}

def get_manager_info(employee_id: str) -> dict:
    """Return the employee's reporting manager information."""
    employee = EMPLOYEES.get(employee_id)
    if not employee:
        return {"status": "Employee not found", "employee_id": employee_id}

    manager = MANAGERS.get(employee["manager_id"])
    if not manager:
        return {"status": "Manager information not found", "employee_id": employee_id}
    return {"employee_id": employee_id, "manager": manager}

def get_job_openings() -> dict:
    """Return currently available internal job openings."""
    return {"job_openings": JOB_OPENINGS}

def get_training_courses() -> dict:
    """Return available employee training courses."""
    return {"training_courses": TRAINING_COURSES}

def get_payroll_status(employee_id: str) -> dict:
    """Return payroll processing status for an employee."""
    status = PAYROLL_STATUS.get(employee_id)
    if not status:
        return {"status": "Payroll information not found", "employee_id": employee_id}
    return {"employee_id": employee_id, **status}

# -------------------------------------------------------------------
# Tool definitions provided to the LLM.
# The LLM selects tools; it does not execute Python functions itself.
# -------------------------------------------------------------------

def employee_id_parameter():
    return {
        "type": "object",
        "properties": {
            "employee_id": {
                "type": "string",
                "description": "The employee's ID, such as E002."
            }
        },
        "required": ["employee_id"],
        "additionalProperties": False,
    }


def department_id_parameter():
    return {
        "type": "object",
        "properties": {
            "department_id": {
                "type": "string",
                "description": "The department ID, such as D001."
            }
        },
        "required": ["department_id"],
        "additionalProperties": False,
    }


def no_parameter_schema():
    return {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }


available_tools = [
    {
        "type": "function",
        "name": "get_employee_info",
        "description": "Get an employee's basic profile information.",
        "parameters": employee_id_parameter(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_salary_info",
        "description": "Get the current salary information of an employee.",
        "parameters": employee_id_parameter(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_leave_balance",
        "description": "Get an employee's remaining leave balances.",
        "parameters": employee_id_parameter(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_attendance_info",
        "description": "Get an employee's attendance information.",
        "parameters": employee_id_parameter(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_department_info",
        "description": "Get information about a department.",
        "parameters": department_id_parameter(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_company_holidays",
        "description": "List upcoming company holidays.",
        "parameters": no_parameter_schema(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_manager_info",
        "description": "Get the reporting manager of an employee.",
        "parameters": employee_id_parameter(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_job_openings",
        "description": "List current internal job openings.",
        "parameters": no_parameter_schema(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_training_courses",
        "description": "List available employee training courses.",
        "parameters": no_parameter_schema(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_payroll_status",
        "description": "Get an employee's payroll processing status.",
        "parameters": employee_id_parameter(),
        "strict": True,
    },
]


# -------------------------------------------------------------------
# Pure Python tool registry and generic dispatcher.
# Add a function here when adding a new tool.
# -------------------------------------------------------------------

tool_registry = {
    "get_employee_info": get_employee_info,
    "get_salary_info": get_salary_info,
    "get_leave_balance": get_leave_balance,
    "get_attendance_info": get_attendance_info,
    "get_department_info": get_department_info,
    "get_company_holidays": get_company_holidays,
    "get_manager_info": get_manager_info,
    "get_job_openings": get_job_openings,
    "get_training_courses": get_training_courses,
    "get_payroll_status": get_payroll_status,
}

def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Look up and execute a tool using its name and parsed arguments."""
    function = tool_registry.get(tool_name)

    if function is None:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        return function(**arguments)
    except TypeError as exc:
        # Handles mismatched arguments; production code should log this.
        return {"error": f"Invalid arguments for {tool_name}: {exc}"}


# -------------------------------------------------------------------
# Agent loop: LLM selects tool -> Python executes -> tool result is
# sent back to LLM. The loop continues until the LLM gives a final
# user-facing answer.
# -------------------------------------------------------------------

def run_agent(user_request: str, employee_id: str) -> str:
    instructions = f"""
You are a friendly Employee HR Assistant who communicates like a real
human HR colleague.

AUTHENTICATION AND SECURITY:
- The authenticated employee ID for this session is {employee_id}.
- Use this ID for employee-specific tool calls.
- Never accept a different employee ID from the user's message as
  authorization to access another employee's records.

TOOL USAGE:
- Use the available tools whenever HR information is required.
- You may call multiple tools to fulfill a request.
- Never invent HR information.
- Use only information returned by the tools.
- If the request is outside the tools' capabilities, explain that politely.

CONVERSATIONAL BEHAVIOR:
Your responses MUST sound like natural human conversation.

STRICT RESPONSE RULES:
1. Do NOT use Markdown headings such as "Your Profile",
   "Your Manager", or "Leave Balance".
2. Do NOT use bullet points or numbered lists unless explicitly
   requested by the user.
3. Do NOT present information as a report, table, or data sheet.
4. NEVER simply copy the structure of the tool results.
5. Convert the retrieved information into natural sentences.
6. When multiple tools are called, combine their results into
   a smooth, coherent conversational response.
7. Use contractions and friendly expressions where appropriate.
8. Avoid robotic introductions such as "Here is your information".
9. Do not mention tool calls or internal processing.
10. Keep the response concise and human-like.

EXAMPLE OF DESIRED BEHAVIOR:

You will get tool results like this, but your response should be a natural, human-like summary:
Employee: John Doe
Designation: Senior Software Engineer
Joining date: April 12, 2021
Manager: Mr. Rahman
Manager designation: Engineering Manager
Annual leave: 15 days
Sick leave: 8 days
Casual leave: 4 days

GOOD RESPONSE:
"Hi John! You're a Senior Software Engineer and joined us on
April 12, 2021. You report to Mr. Rahman, our Engineering Manager.

As for your leave, you've got 15 days of annual leave,
8 days of sick leave, and 4 days of casual leave remaining.
Hope that helps!"

BAD RESPONSE:
"### Your Profile
- Name: John Doe
- Designation: Senior Software Engineer

### Your Manager
- Name: Mr. Rahman

### Leave Balance
- Annual leave: 15 days"

Always follow the GOOD RESPONSE style.
"""

    # LLM Call 1: understand request and choose tool(s), or answer directly.
    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=user_request,
        tools=available_tools,
    )

    # Continue until the model returns a final answer with no function calls.
    while True:
        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            return response.output_text

        tool_outputs = []

        # Pure Python: execute each function call returned by the LLM.
        for call in function_calls:
            arguments = json.loads(call.arguments)

            # For employee-specific tools, enforce session employee ID.
            if "employee_id" in arguments:
                arguments["employee_id"] = employee_id

            result = execute_tool(call.name, arguments)

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            })

        # LLM Call: process tool results, potentially select more tools,
        # or produce the final user-friendly response.
        response = client.responses.create(
            model=MODEL,
            instructions=instructions,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=available_tools)
        
def main() -> None:
    # In production, employee_id must come from authenticated session
    # identity, not from arbitrary user-entered text.
    authenticated_employee_id = "E002"

    user_request = (
        "Tell me about my profile, my manager, and my leave balance."
    )

    final_answer = run_agent(
        user_request=user_request,
        employee_id=authenticated_employee_id,
    )

    print("\nHR Assistant:")
    print(final_answer)

if __name__ == "__main__":
    main()
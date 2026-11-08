
company = [
    {
        "id": 101,
        "name": "Rahim",
        "department": "IT",
        "skills": ["Python", "Django", "SQL"],
        "salary_history": (50000, 55000, 60000),
        "projects": [
            {"name": "HR System", "duration": 6},
            {"name": "Payroll System", "duration": 3}
        ]
    },
    {
        "id": 102,
        "name": "Karim",
        "department": "HR",
        "skills": ["Recruitment", "Excel"],
        "salary_history": (40000, 45000),
        "projects": [
            {"name": "Recruitment Portal", "duration": 4}
        ]
    },
    {
        "id": 103,
        "name": "Hasan",
        "department": "Finance",
        "skills": ["Accounting", "Excel", "Power BI"],
        "salary_history": (45000, 50000, 55000),
        "projects": [
            {"name": "Budget System", "duration": 5},
            {"name": "Financial Dashboard", "duration": 2},
            {"name": "Audit System", "duration": 4}
        ]
    }
]


# 1. Total Salary
total_salary = sum(
    salary
    for employee in company
    for salary in employee["salary_history"]
)


# 2. Average Salary
salary_count = sum(
    len(employee["salary_history"])
    for employee in company
)

average_salary = total_salary / salary_count


# 3. Total Project Duration
total_duration = sum(
    project["duration"]
    for employee in company
    for project in employee["projects"]
)


# 4. Average Project Duration
project_count = sum(
    len(employee["projects"])
    for employee in company
)

average_duration = total_duration / project_count


# Display Results
print("Total Salary:", total_salary)
print("Average Salary:", average_salary)
print("Total Project Duration:", total_duration)
print("Average Project Duration:", average_duration)

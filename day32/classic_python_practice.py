
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


# Classic Python Way

# Initialize variables
total_salary = 0
salary_count = 0

total_duration = 0
project_count = 0

for employee in company:

    # Calculate Salary
    for salary in employee["salary_history"]:
        total_salary += salary
        salary_count += 1

    # Calculate Project Duration
    for project in employee["projects"]:
        total_duration += project["duration"]
        project_count += 1


# Calculate Average
average_salary = total_salary / salary_count
average_duration = total_duration / project_count


# Display Results
print("Total Salary:", total_salary)
print("Average Salary:", average_salary)
print("Total Project Duration:", total_duration)
print("Average Project Duration:", average_duration)


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



# Lambda Expression Way

# 1. Total Salary
total_salary = sum(
    map(
        lambda salary: sum(salary["salary_history"]),
        company
    )
)

# 2. Average Salary
total_salary_count = sum(
    map(
        lambda employee: len(employee["salary_history"]),
        company
    )
)

average_salary = total_salary / total_salary_count


# 3. Total Project Duration
total_duration = sum(
    map(
        lambda employee: sum(
            map(
                lambda project: project["duration"],
                employee["projects"]
            )
        ),
        company
    )
)


# 4. Average Project Duration
project_count = sum(
    map(
        lambda employee: len(employee["projects"]),
        company
    )
)

average_duration = total_duration / project_count


# Display Results
print("Total Salary:", total_salary)
print("Average Salary:", average_salary)
print("Total Project Duration:", total_duration)
print("Average Project Duration:", average_duration)

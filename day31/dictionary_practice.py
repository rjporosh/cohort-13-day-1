
# Step 1: Create an Employee Dictionary
employees = {
    101: {"name": "Rahim", "department": "IT", "salary": 60000},
    102: {"name": "Karim", "department": "HR", "salary": 45000},
    103: {"name": "Hasan", "department": "IT", "salary": 75000},
    104: {"name": "Sakib", "department": "Finance", "salary": 55000},
    105: {"name": "Nabil", "department": "HR", "salary": 50000}
}

# Step 2: Display all employees
print("=== Employee List ===")

for emp_id, info in employees.items():
    print(emp_id, info)

# Step 3: Access employee information using get()
print("\n=== Get Employee Information ===")
print("Employee 101:", employees.get(101))

# Step 4: Update employee information
employees[102].update({
    "name": "Karim Ahmed",
    "department": "Finance",
    "salary": 65000
})

print("\n=== After Updating Employee 102 ===")
print(employees.get(102))

# Step 5: Display all Employee IDs using keys()
print("\n=== Employee IDs ===")
print(list(employees.keys()))

# Step 6: Display all employee records using values()
print("\n=== Employee Information ===")
print(list(employees.values()))

# Step 7: Display Employee ID and Information using items()
print("\n=== All Employee Records ===")
for emp_id, info in employees.items():
    print(f"ID: {emp_id}, Name: {info['name']}, "
          f"Department: {info['department']}, Salary: {info['salary']}")

# Step 8: Calculate total salary
total_salary = sum(
    info["salary"] for info in employees.values()
)

print("\nTotal Salary:", total_salary)

# Step 9: Calculate department-wise salary
department_salary = {}

for info in employees.values():
    department = info["department"]
    salary = info["salary"]

    department_salary[department] = (
        department_salary.get(department, 0) + salary
    )

print("\n=== Department-wise Salary ===")
for department, total in department_salary.items():
    print(f"{department}: {total}")

# Step 10: Create a dictionary of employees
# whose salary is greater than or equal to 55000
high_salary_employees = {
    emp_id: info
    for emp_id, info in employees.items()
    if info["salary"] >= 55000
}

print("\n=== Employees with Salary >= 55000 ===")
for emp_id, info in high_salary_employees.items():
    print(emp_id, info)

# Step 11: Remove an employee using pop()
removed_employee = employees.pop(105)

print("\n=== Removed Employee ===")
print(removed_employee)

print("\n=== Final Employee Dictionary ===")
print(employees)

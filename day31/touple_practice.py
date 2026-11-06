
# Step 1: Create two tuples
expenditure = (500, 1200, 800, 1500, 300)
salary = (15000, 20000, 18000, 25000, 12000)

# salary.insert(2,19000) # Update the salary at index 2 with the new value
# salary[2] = 19000  # Update the salary at index 2 with the new value
print(salary)  # Output: (15000, 20000, 19000, 25000, 12000)
# Step 2: Combine both tuples
all_amounts = expenditure + salary

print(type(all_amounts))  # Output: <class 'tuple'>
# Step 3: Calculate total
total = sum(all_amounts)

# Step 4: Find lowest and highest expenditure
lowest_expenditure = min(expenditure)
highest_expenditure = max(expenditure)

# Step 5: Find lowest and highest salary
lowest_salary = min(salary)
highest_salary = max(salary)

# Step 6: Display results
print("Expenditure Tuple:", expenditure)
print("Salary Tuple:", salary)

print("\nCombined Tuple:", all_amounts)
print("Total Income and Expenditure:", total)

print("\n--- Expenditure Details ---")
print("Lowest Expenditure:", lowest_expenditure)
print("Highest Expenditure:", highest_expenditure)

print("\n--- Salary Details ---")
print("Lowest Salary:", lowest_salary)
print("Highest Salary:", highest_salary)

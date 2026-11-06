
# Step 1: Create two lists
expenditure = [500, 1200, 800, 1500, 300]
salary = [15000, 20000, 18000, 25000, 12000]

# Step 2: Combine both lists
all_amounts = expenditure + salary

# Step 3: Calculate total
total = sum(all_amounts)

# Step 4: Find minimum and maximum values
lowest_expenditure = min(expenditure)
highest_expenditure = max(expenditure)

lowest_salary = min(salary)
highest_salary = max(salary)

# Step 5: Display results
print("Expenditure List:", expenditure)
print("Salary List:", salary)

print("\nCombined List:", all_amounts)
print("Total Income and Expenditure:", total)

print("\n--- Expenditure Details ---")
print("Lowest Expenditure:", lowest_expenditure)
print("Highest Expenditure:", highest_expenditure)

print("\n--- Salary Details ---")
print("Lowest Salary:", lowest_salary)
print("Highest Salary:", highest_salary)

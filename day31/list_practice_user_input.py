
# Step 1: Create two lists
expenditure = [500, 1200, 800, 1500, 300]
salary = [15000, 20000, 18000, 25000, 12000]

# Step 2: Take user input for expenditure
new_expenditure = int(input("Enter a new expenditure amount: "))
expenditure.append(new_expenditure)

# Step 3: Take user input for salaryclea
new_salary = int(input("Enter a new salary amount: "))
# salary.insert(2, new_salary)
salary[2] = new_salary  # Update the salary at index 2 with the new value

# Step 4: Combine both lists
all_amounts = expenditure + salary

# Step 5: Calculate total
total = sum(all_amounts)

# Step 6: Find minimum and maximum values
lowest_expenditure = min(expenditure)
highest_expenditure = max(expenditure)

lowest_salary = min(salary)
highest_salary = max(salary)

# Step 7: Display results
print("\nExpenditure List:", expenditure)
print("Salary List:", salary)

print("\nCombined List:", all_amounts)
print("Total Income and Expenditure:", total)

print("\n--- Expenditure Details ---")
print("Lowest Expenditure:", lowest_expenditure)
print("Highest Expenditure:", highest_expenditure)

print("\n--- Salary Details ---")
print("Lowest Salary:", lowest_salary)
print("Highest Salary:", highest_salary)

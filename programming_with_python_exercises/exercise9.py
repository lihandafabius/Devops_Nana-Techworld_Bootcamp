import pandas as pd # requires openpyxl to read excel files

df = pd.read_excel("employees.xlsx")
print(df.info())
print(df.head())

employee_sorted = df.sort_values("Years of Experience", ascending=False)
print(employee_sorted)
# saving
employee_sorted.to_excel("employee_sorted.xlsx", index=False)

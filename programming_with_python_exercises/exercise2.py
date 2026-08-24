employee = {
  "name": "Tim",
  "age": 30,
  "birthday": "1990-03-10",
  "job": "DevOps Engineer"
}

employee.update({"job": "Software Engineer"})
print(employee)

employee.pop("age")
print(employee)

for key, value in employee.items():
    print(f"{key}:{value}")

# merging dictionaries
dict_one = {'a': 100, 'b': 400}
dict_two = {'x': 300, 'y': 200}

# method 1
# merged_dict = dict_one.copy()
# merged_dict.update(dict_two)
# print(merged_dict)

# method 2
# merged_dict = dict_one.copy()
# for key, value in dict_two.items():
#     merged_dict[key] = value
# print(merged_dict)

# method 3
merged_dict = dict_one | dict_two
print(merged_dict)

# sum of all values
list_of_merged_dict_values = merged_dict.values()
total_values = 0
for value in list_of_merged_dict_values:
    total_values += value
print(total_values)

# max and min values
max_value = max(list_of_merged_dict_values)
min_value = min(list_of_merged_dict_values)
print(f"maximum value of the dict is {max_value} and the minimum vlaue of the dict is {min_value}")


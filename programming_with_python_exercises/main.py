from exercise4 import get_youngest_employee, print_even_numbers, calculate_upper_and_lower_case_letters
employees = [{
  "name": "Tina",
  "age": 30,
  "birthday": "1990-03-10",
  "job": "DevOps Engineer",
  "address": {
    "city": "New York",
    "country": "USA"
  }
},
{
  "name": "Tim",
  "age": 35,
  "birthday": "1985-02-21",
  "job": "Developer",
  "address": {
    "city": "Sydney",
    "country": "Australia"
  }
}
]

result = get_youngest_employee(employees)
print(result)

string_input = input("Please enter your string: ")
lower, upper = calculate_upper_and_lower_case_letters(string_input)
print(f"Lower case Letters: {lower}")
print(f"Upper case Letters: {upper}")

input_list = input("Please enter your number list: ")
number_list = [int(number) for number in input_list.split(",")]
even, odd = print_even_numbers(number_list)
print(f"even numbers {even}")
print(f"odd numbers {odd}")
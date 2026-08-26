def calculate_upper_and_lower_case_letters(string_input):
    upper_case_letter_count = 0
    lower_case_letter_count = 0
    for letter in string_input:
        if letter.isupper():
            upper_case_letter_count += 1
        elif letter.islower():
            lower_case_letter_count += 1
    return lower_case_letter_count, upper_case_letter_count


def print_even_numbers(number_list):
    even_numbers = []
    odd_numbers = []
    for number in number_list:
        if int(number) % 2 == 0:
            even_numbers.append(number)
        else:
            odd_numbers.append(number)
    return even_numbers, odd_numbers



def get_youngest_employee(employees):
    age_list = []
    for employee in employees:
        age = employee["age"]
        age_list.append(age)

    youngest_age = min(age_list)

    for employee in employees:
        if employee["age"] == youngest_age:
            return employee["name"]




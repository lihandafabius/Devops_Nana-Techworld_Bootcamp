# calculation_to_units = 24
# name_of_unit = "hours"
from unittest import result


# try:
#     while True:
#         no_of_days = int(input("Please enter number of days to convert: "))
#         if no_of_days < 0 or no_of_days == 0:
#             print("Number of days should be positive and greater than 0")
#         else:
#
#             def conversion_days_to_units(days):
#                 calculation_to_units = ""
#                 name_of_unit = str(input("Please enter name of unit: "))
#
#                 if name_of_unit == "hours":
#                     calculation_to_units = 24
#                 elif name_of_unit == "minutes":
#                     calculation_to_units = 60 * 24
#                 elif name_of_unit == "seconds":
#                     calculation_to_units = 60 * 60 * 24
#                 else:
#                     print("Please provide units")
#
#                 return f"{days} days are {days * calculation_to_units} {name_of_unit}"
#
#
#             result = conversion_days_to_units(no_of_days)
#             print(result)
#             print("All good")
# except ValueError:
#     print("Please provide number of days as numbers/intergers")


# try:
#
#     no_of_days = input("Please enter number of days to convert: ")
#
#     def conversion_days_to_units(days):
#         calculation_to_units = ""
#         name_of_unit = str(input("Please enter name of unit: "))
#
#         if name_of_unit == "hours":
#             calculation_to_units = 24
#         elif name_of_unit == "minutes":
#             calculation_to_units = 60 * 24
#         elif name_of_unit == "seconds":
#             calculation_to_units = 60 * 60 * 24
#         else:
#             print("Please provide units")
#
#         return f"{days} days are {days * calculation_to_units} {name_of_unit}"
#
#
#     for day in no_of_days.split(","):
#         result = conversion_days_to_units(day)
#         print(result)
#         print("All good")
# except ValueError:
#     print("Please provide number of days as numbers/intergers")


# def conversion_days_to_units(days, name_of_unit):
#     if name_of_unit == "hours":
#         calculation_to_units = 24
#     elif name_of_unit == "minutes":
#         calculation_to_units = 60 * 24
#     elif name_of_unit == "seconds":
#         calculation_to_units = 60 * 60 * 24
#     else:
#         print("Please provide units")
#
#     return f"{days} days are {days * calculation_to_units} {name_of_unit}"
#
# user_input = input("Please provide list to convert: ")
# no_of_days = user_input.split(",")
# print(no_of_days)
# no_of_days = set(no_of_days)
# print(no_of_days)
# name_of_unit = str(input("Please enter name of unit: "))
# for days in no_of_days:
#     try:
#         result = conversion_days_to_units(int(days), name_of_unit)
#         print(result)
#     except ValueError:
#         print("Please provide number of days as numbers/intergers")

def conversion_days_to_units(days, name_of_unit):
    if name_of_unit == "hours":
        calculation_to_units = 24
    elif name_of_unit == "minutes":
        calculation_to_units = 60 * 24
    elif name_of_unit == "seconds":
        calculation_to_units = 60 * 60 * 24
    else:
        print("Please provide units")

    return f"{days} days are {int(days) * calculation_to_units} {name_of_unit}"

user_input = ""
while user_input != "exit":
    user_input = input("Please enter number of days and conversion unit! eg 20:hours \n")
    if user_input == "exit":
        break
    days_and_unit = user_input.split(":")
    print(days_and_unit)
    days_and_unit_dictionary = {"days":days_and_unit[0], "units":days_and_unit[1]}
    print(days_and_unit_dictionary)
    result = conversion_days_to_units(days_and_unit_dictionary["days"], days_and_unit_dictionary["units"])
    print(result)

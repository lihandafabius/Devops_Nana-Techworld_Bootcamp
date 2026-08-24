from datetime import datetime


def check_time_remaining_till_birthday(birthday):
    today = datetime.today()

    # Create this year's birthday
    next_birthday = datetime(
        today.year,
        birthday.month,
        birthday.day
    )

    # If birthday has already happened this year,
    # use next year's birthday
    if next_birthday < today:
        next_birthday = datetime(
            today.year + 1,
            birthday.month,
            birthday.day
        )

    time_remaining = next_birthday - today

    days_remaining = time_remaining.days
    hours_remaining = time_remaining.seconds // 3600 # // means floor division, divides two numbers and returns the whole-number part, removing the decimal
    minutes_remaining = (time_remaining.seconds % 3600) // 60

    return f"You have {days_remaining} days, {int(hours_remaining)} hours, {int(minutes_remaining)} minutes until your birthday."


birthday_input = input("Please enter your birthday date (DD/MM/YYYY): ")

while True:
    try:
        birthday = datetime.strptime(birthday_input, "%d/%m/%Y")
        result = check_time_remaining_till_birthday(birthday)
        print(result)
        break

    except ValueError:
        print("please enter birthday in the right format: DD/MM/YYYY")
        birthday_input = input("Please re-enter your birthday date (DD/MM/YYYY): ")


e
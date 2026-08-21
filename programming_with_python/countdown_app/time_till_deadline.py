from datetime import datetime


def calculate_time_till_deadline(checked_date):
    start_time = datetime.today()
    end_time = checked_date

    time_till_deadline = end_time - start_time
    return time_till_deadline.days

def validate_date(deadline):

        checked_date = datetime.strptime(deadline, "%d/%m/%Y")
        return checked_date



user_input = input("Please enter your goal and deadline for your project:")
input_list = user_input.split(":")
user_input_dictionary = {
    "goal":input_list[0],
    "deadline":input_list[1]
}
goal = user_input_dictionary["goal"]
deadline = user_input_dictionary["deadline"]
while True:
    try:

        valid_date = validate_date(deadline)
        days = calculate_time_till_deadline(valid_date)
        print(f"You have {days} days remaining to {goal}")
        break

    except ValueError:
        print("Please enter the date in the correct format: DD/MM/YYYY")
        deadline = input("Enter deadline: ")






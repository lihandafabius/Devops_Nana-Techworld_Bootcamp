from datetime import datetime
def calculate_time_till_deadline(checked_date):
    start_time = datetime.today()
    end_time = checked_date

    time_till_deadline = end_time - start_time
    return time_till_deadline.days

user_input = input("Please enter your goal and deadline for your project:")
input_list = user_input.split(":")
user_input_dictionary = {
    "goal":input_list[0],
    "deadline":input_list[1]
}
goal = user_input_dictionary["goal"]
deadline = user_input_dictionary["deadline"]
checked_date = datetime.strptime(deadline, "%d/%m/%Y")
days = calculate_time_till_deadline(checked_date)

print(f"You have {days} days remaining to {goal}")




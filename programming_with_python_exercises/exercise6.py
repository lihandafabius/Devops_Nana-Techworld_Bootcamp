import random
random_number = random.randint(1, 10)
while True:
    user_input = int(input("Guess a number between 1 and 9: "))
    if user_input > random_number:
        print("Your guess is too high")
    elif user_input < random_number:
        print("Your guess is too low")
    elif user_input == random_number:
        print("You Won!")
        break



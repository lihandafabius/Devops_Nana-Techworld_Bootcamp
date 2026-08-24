no_of_calculations = 0
while True:
    user_input = input("Type 'exit' to quit or press Enter to continue: ")

    if user_input.lower() == "exit":
        print("Calculator closed.")
        break

    while True:
        try:
            num1 = int(input("Please enter first number to perform operation: "))
            break
        except ValueError:
            print("Only numbers allowed. Please re-enter num1: ")
    while True:
        try:
            num2 = int(input("Please enter second number to perform operation: "))
            break
        except ValueError:
            print("Only numbers allowed. Please re-enter a num2: ")

    operation_input = input("Please enter operation you want to perform from the choices [plus, minus, multiply, divide]: ")
    if operation_input == "plus":
        result = num1 + num2
        print(result)
    elif operation_input == "minus":
        result = num1 - num2
        print(result)
    elif operation_input == "multiply":
        result = num1 * num2
        print(result)
    elif operation_input == "divide":
        while True:
            try:
                result = num1 / num2
                print(result)
                break
            except ZeroDivisionError:
                print("You can not divide by zero. Please enter a non-zero number.")
                while True:
                    try:
                        num2 = int(input("Please re-enter second number: "))
                        break
                    except ValueError:
                        print("Only numbers allowed. Please enter a number.")
    else:
        print("Invalid Operation. Please enter a valid operation from the choices.")
    no_of_calculations += 1

print(f"number of calculation:{no_of_calculations}")
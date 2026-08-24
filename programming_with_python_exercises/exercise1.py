user_input = int(input("Please enter your number: "))
my_list = [1, 2, 2, 4, 4, 5, 6, 8, 10, 13, 22, 35, 52, 83]
new_list = []
for element in my_list:
    if element > user_input:
        new_list.append(element)
print(new_list)


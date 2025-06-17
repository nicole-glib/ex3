if __name__ == '__main__':
    history = []
    continue1 = 1
    #the instructions for the calculator
    print("Welcome to the Python Calculator!\n"
          "You can perform the following operations:\n"
          "1: Addition\n"
          "2: Subtraction\n"
          "3: Multiplication\n"
          "4: Division\n"
          "5: Check which number is greater\n"
          )
    #calculates max 5 times
    calculation_num = 0
    while calculation_num < 5:
        if not continue1:
            break
        # ask the user for the first and second numbers
        num1 = round(float(input("Enter the first number: ")),2)
        num2 = round(float(input("Enter the second number: ")),2)
        # ask the user to select an operation to perform
        while True:
            str1 = ""
            operation_number = input("select operation (1-5): ")
            # preform the appropriate operation corresponding to the right number

            # recives two numbers
            # gives the calculation based on the operator
            if operation_number == "1":
                operator = '+'
                str1 = str(num1) + ' + ' + str(num2) + ' = ' + str(round(num1 + num2, 2))
                break

            elif operation_number == "2":
                operator = '-'
                str1 = str(num1) + ' - ' + str(num2) + ' = ' + str(round(num1 - num2, 2))
                break

            elif operation_number == "3":
                operator = '*'
                str1 = str(num1) + ' * ' + str(num2) + ' = ' + str(round(num1 * num2, 2))
                break

            elif operation_number == "4":
                operator = '/'
                if num2 == 0:
                    calculation_num -= 1
                    print("Cannot divide by zero!\n")
                else:
                    str1 = str(num1) + ' / ' + str(num2) + ' = ' + str(round(num1 / num2, 2))
                break

                # compares two numbers
                # returns string that tell which number is higher
            elif operation_number == "5":
                comparison_conclusion = ""
                if num1 < num2:
                    comparison_conclusion = str(num2) + " is greater than " + str(num1)
                elif num1 > num2:
                    comparison_conclusion = str(num1) + " is greater than " + str(num2)
                else:
                    comparison_conclusion = "Both numbers are equal."
                str1 = comparison_conclusion
                break

            else:
                print("Invalid selection! Please choose an option from 1 to 5.")
        # print the result of the operation in operations 1-4.
        if str1 != "":
            print(str1)
            # add the calculation to the calculation history list if user inputs 1, don't add if user inputs 0.
            # and re-ask user for input if its niether 0 or 1.
            while True:
                save = input("Do you want to save this calculation to history? (1-Yes, 0-No): ")
                if save == "1":
                    history.append(str1)
                    break
                elif save == "0":
                    break
                else:
                    print("Invalid input! Please enter 1 to save or 0 not to save.")
            print()
            if calculation_num == 4:
                print("You have reached the maximum number of calculations allowed.\n")
                calculation_num += 1
                break
        # exit the calculator after 5 calculations or if the user inputs "0".
        # division by 0 is not counted as a calculation.
        while True:
            continue1 = input("Do you want to continue? (1-Yes, 0-No): ")
            if continue1 == "1":
                continue1 = 1
                break
            elif continue1 == "0":
                continue1 = 0
                break
            else:
                print("Invalid input! Please enter 1 to continue or 0 to exit.", end="\n\n")
        print()

        calculation_num += 1
    # print an exit message and the number of calculations made.
    print("Exiting the calculator...")
    print("You performed", calculation_num, "calculations. Thank you and goodbye!\n")
    # if the calculation history list is not empty, print it.
    if history:
        print("Calculation History:")
        for item in history:
            print(item)

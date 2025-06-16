import math

def calculator():
    print("Welcome to Advanced Calculator!")

    while True:
        print("\nSelect operation:")
        print("1. Addition (+)")
        print("2. Subtraction (-)")
        print("3. Multiplication (*)")
        print("4. Division (/)")
        print("5. Power (x^y)")
        print("6. Modulus (%)")
        print("7. Floor Division (//)")
        print("8. Square Root")
        print("9. Trigonometric Functions (sin, cos, tan)")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == '0':
            print("Exiting calculator. Goodbye!")
            break

        try:
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))

                if choice == '1':
                    print("Result:", num1 + num2)
                elif choice == '2':
                    print("Result:", num1 - num2)
                elif choice == '3':
                    print("Result:", num1 * num2)
                elif choice == '4':
                    if num2 != 0:
                        print("Result:", num1 / num2)
                    else:
                        print("Error! Cannot divide by zero.")
                elif choice == '5':
                    print("Result:", num1 ** num2)
                elif choice == '6':
                    print("Result:", num1 % num2)
                elif choice == '7':
                    print("Result:", num1 // num2)

            elif choice == '8':
                num = float(input("Enter number: "))
                if num >= 0:
                    print("Square Root:", math.sqrt(num))
                else:
                    print("Error! Cannot take square root of negative number.")

            elif choice == '9':
                angle = float(input("Enter angle in degrees: "))
                radians = math.radians(angle)
                print("sin(", angle, ") =", math.sin(radians))
                print("cos(", angle, ") =", math.cos(radians))
                print("tan(", angle, ") =", math.tan(radians))

            else:
                print("Invalid choice!")

        except ValueError:
            print("Invalid input! Please enter numeric values.")

# Run the calculator
calculator()

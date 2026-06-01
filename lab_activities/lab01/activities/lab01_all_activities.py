"""
CSC462 Lab 01 - All Solved Activities (1-7)
Run this file and choose an activity number from the menu.
"""

import random


def activity1_even_odd():
    """Take an integer and check if it is even or odd."""
    num = int(input("Enter an integer: "))
    if num % 2 == 0:
        print(f"{num} is even.")
    else:
        print(f"{num} is odd.")


def activity2_sum_until_zero():
    """Accept integers until 0; display sum (0 is not included)."""
    total = 0
    while True:
        value = int(input("Enter an integer (0 to stop): "))
        if value == 0:
            break
        total += value
    print(f"Sum of entered values: {total}")


def activity3_prime_check():
    """Check if the entered integer is prime."""
    num = int(input("Enter an integer: "))
    if num < 2:
        is_prime = False
    else:
        is_prime = True
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
    if is_prime:
        print(f"{num} is a prime number.")
    else:
        print(f"{num} is not a prime number.")


def activity4_sum_five_integers():
    """Accept 5 integers and display their sum."""
    total = 0
    for i in range(1, 6):
        value = int(input(f"Enter integer {i} of 5: "))
        total += value
    print(f"Sum of 5 integers: {total}")


def activity5_sum_zero_to_ten():
    """Sum values 0 through 10 using a while loop."""
    total = 0
    i = 0
    while i <= 10:
        total += i
        i += 1
    print(f"Sum of values from 0 to 10: {total}")


def activity6_keyboard_input():
    """Take name, job, and number from keyboard."""
    name = input("What is your name? ")
    print("Hello " + name)
    job = input("What is your job? ")
    print("Your job is " + job)
    num = input("Give me a number? ")
    print("You said: " + str(num))


def activity7_guess_number():
    """Guess random number 1-9; type 'exit' to quit."""
    secret = random.randint(1, 9)
    guesses = 0
    print("Alright... Guess a number between 1 and 9 (type 'exit' to quit).")
    while True:
        guess = input("What is your lucky number? ").strip()
        if guess.lower() == "exit":
            print("Better luck next time.")
            print(f"You took {guesses} guess(es).")
            break
        try:
            value = int(guess)
        except ValueError:
            print("Please enter a number or 'exit'.")
            continue
        guesses += 1
        if value < secret:
            print("Wrong, too low.")
        elif value > secret:
            print("Wrong, too high.")
        else:
            print(f"Yes, that's the one, {secret}.")
            if guesses < 2:
                print(f"Impressive, only {guesses} try.")
            elif guesses < 10:
                print(f"Pretty good, {guesses} tries.")
            else:
                print(f"Bad, {guesses} tries.")
            break


def main():
    activities = {
        1: ("Even or Odd", activity1_even_odd),
        2: ("Sum until 0", activity2_sum_until_zero),
        3: ("Prime Check", activity3_prime_check),
        4: ("Sum of 5 Integers", activity4_sum_five_integers),
        5: ("Sum 0 to 10", activity5_sum_zero_to_ten),
        6: ("Keyboard Input", activity6_keyboard_input),
        7: ("Guess the Number", activity7_guess_number),
    }

    print("=" * 40)
    print("  CSC462 Lab 01 - All Activities")
    print("=" * 40)
    for num, (title, _) in activities.items():
        print(f"  {num}. {title}")
    print("  0. Exit")
    print("=" * 40)

    choice = input("Select activity (1-7): ").strip()
    if choice == "0":
        return
    if choice.isdigit() and 1 <= int(choice) <= 7:
        print()
        activities[int(choice)][1]()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

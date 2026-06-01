"""
Activity 7: Guess a random number between 1 and 9.
Extras: type 'exit' to quit; print guess count when the game ends.
"""

import random

MINIMUM = 1
MAXIMUM = 9
secret = random.randint(MINIMUM, MAXIMUM)
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

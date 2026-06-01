"""Activity 3: Check whether a user-entered integer is prime."""

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

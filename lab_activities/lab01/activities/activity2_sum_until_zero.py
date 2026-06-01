"""Activity 2: Accept integers until 0 is entered; display sum of values."""

total = 0

while True:
    value = int(input("Enter an integer (0 to stop): "))
    if value == 0:
        break
    total += value

print(f"Sum of entered values: {total}")

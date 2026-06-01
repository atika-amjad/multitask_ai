"""
CSC462 Lab 01 - All Graded Lab Tasks (1-5)
Run this file and choose a task number from the menu.
"""


def task1_reverse_digits():
    """Reverse the digits of an integer (e.g. 12345 -> 54321)."""
    num = int(input("Enter an integer: "))
    reversed_num = int(str(abs(num))[::-1])
    if num < 0:
        reversed_num = -reversed_num
    print(f"Reversed number: {reversed_num}")


def task2_sum_even_odd():
    """Read integers until user stops; print sum of evens and sum of odds."""
    print("Enter integers one per line (empty line to finish):")
    even_sum = 0
    odd_sum = 0
    while True:
        line = input().strip()
        if line == "":
            break
        value = int(line)
        if value % 2 == 0:
            even_sum += value
        else:
            odd_sum += value
    print(f"Sum of even integers: {even_sum}")
    print(f"Sum of odd integers: {odd_sum}")


def task3_fibonacci():
    """Display Fibonacci series for given number of terms (starting 0, 1)."""
    n = int(input("How many Fibonacci terms to display? "))
    if n <= 0:
        print("No terms to display.")
        return
    a, b = 0, 1
    series = []
    for _ in range(n):
        series.append(a)
        a, b = b, a + b
    print(" ".join(str(x) for x in series))


def task4_grade_from_marks():
    """Display grade from marks (1-100)."""
    marks = int(input("Enter marks (1-100): "))
    if marks < 1 or marks > 100:
        print("Invalid marks. Enter a value between 1 and 100.")
        return
    if marks < 50:
        grade = "F"
    elif marks <= 60:
        grade = "E"
    elif marks <= 70:
        grade = "D"
    elif marks <= 80:
        grade = "C"
    elif marks <= 90:
        grade = "B"
    else:
        grade = "A"
    print(f"Marks: {marks}  →  Grade: {grade}")


def task5_factorial():
    """Calculate factorial of a non-negative integer."""
    n = int(input("Enter a number: "))
    if n < 0:
        print("Factorial is not defined for negative numbers.")
        return
    result = 1
    for i in range(2, n + 1):
        result *= i
    print(f"Factorial of {n} is {result}")


def main():
    tasks = {
        1: ("Reverse Digits", task1_reverse_digits),
        2: ("Sum of Even and Odd Integers", task2_sum_even_odd),
        3: ("Fibonacci Series", task3_fibonacci),
        4: ("Grade from Marks", task4_grade_from_marks),
        5: ("Factorial", task5_factorial),
    }

    print("=" * 40)
    print("  CSC462 Lab 01 - All Tasks")
    print("=" * 40)
    for num, (title, _) in tasks.items():
        print(f"  {num}. {title}")
    print("  0. Exit")
    print("=" * 40)

    choice = input("Select task (1-5): ").strip()
    if choice == "0":
        return
    if choice.isdigit() and 1 <= int(choice) <= 5:
        print()
        tasks[int(choice)][1]()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

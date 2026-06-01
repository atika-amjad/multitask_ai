"""
CSC462 Lab 02 - All Graded Lab Tasks (1-5)
Run this file and choose a task number from the menu.
"""

from math import *  # noqa: F403, F401 — required for Lab Task 3 (pi, sin, cos)


def task1_merge_sorted():
    """Create two lists from user, merge, display in sorted order."""
    n1 = int(input("How many elements in first list? "))
    list1 = [int(input(f"  list1[{i}]: ")) for i in range(n1)]
    n2 = int(input("How many elements in second list? "))
    list2 = [int(input(f"  list2[{i}]: ")) for i in range(n2)]

    merged = list1 + list2
    sorted_merged = sorted(merged)

    print(f"List 1: {list1}")
    print(f"List 2: {list2}")
    print(f"Merged: {merged}")
    print(f"Sorted merged list: {sorted_merged}")


def task2_smallest_largest():
    """Create two lists, merge, find smallest and largest (integers)."""
    n1 = int(input("How many elements in first list? "))
    list1 = [int(input(f"  list1[{i}]: ")) for i in range(n1)]
    n2 = int(input("How many elements in second list? "))
    list2 = [int(input(f"  list2[{i}]: ")) for i in range(n2)]

    merged = list1 + list2
    print(f"Merged list: {merged}")
    print(f"Smallest element: {min(merged)}")
    print(f"Largest element: {max(merged)}")


def task3_derivative_sin():
    """
    Approximate derivative of sin(x) and compare with cos(x).
    Proves sin'(x) = cos(x) using (sin(x+h) - sin(x)) / h.
    """
    step = 0.001
    x_values = []
    x = -pi
    while x <= pi:
        x_values.append(x)
        x += step

    h_values = [0.001, 0.01, 0.1]

    for h in h_values:
        print("\n" + "=" * 60)
        print(f"  h = {h}")
        print("=" * 60)
        print(f"{'x':>10}  {'approx':>12}  {'cos(x)':>12}  {'diff':>12}")
        print("-" * 60)

        max_diff = 0.0
        for x in x_values:
            approx = (sin(x + h) - sin(x)) / h
            actual = cos(x)
            diff = abs(approx - actual)
            max_diff = max(max_diff, diff)
            print(f"{x:10.4f}  {approx:12.6f}  {actual:12.6f}  {diff:12.6f}")

        print("-" * 60)
        print(f"Maximum |approx - cos(x)| for h = {h}: {max_diff:.6f}")

    print("\nObservation:")
    print("  As h increases (0.001 → 0.01 → 0.1), the approximation drifts")
    print("  further from cos(x) because the finite-difference step is too large.")


def task4_birthday_dictionary():
    """Look up a friend's birthday by name."""
    birthdays = {
        "Albert Einstein": "03/14/1879",
        "Benjamin Franklin": "01/17/1706",
        "Ada Lovelace": "12/10/1815",
    }

    print("Welcome to the birthday dictionary. We know the birthdays of:")
    for name in birthdays:
        print(name)

    name = input("\nWho's birthday do you want to look up?\n").strip()
    if name in birthdays:
        print(f"{name}'s birthday is {birthdays[name]}.")
    else:
        print(f"Sorry, we don't have the birthday for {name}.")


def task5_extract_keys():
    """Create a new dictionary by extracting specified keys."""
    sample_dict = {
        "name": "Kelly",
        "age": 25,
        "salary": 8000,
        "city": "New york",
    }
    keys = ["name", "salary"]

    new_dict = {k: sample_dict[k] for k in keys if k in sample_dict}

    print("Given dictionary:")
    print(sample_dict)
    print(f"\nKeys to extract: {keys}")
    print("\nExpected output:")
    print(new_dict)


def main():
    tasks = {
        1: ("Merge Lists & Sort", task1_merge_sorted),
        2: ("Smallest & Largest in Merged List", task2_smallest_largest),
        3: ("Derivative of sin(x) vs cos(x)", task3_derivative_sin),
        4: ("Birthday Dictionary Lookup", task4_birthday_dictionary),
        5: ("Extract Keys from Dictionary", task5_extract_keys),
    }

    print("=" * 45)
    print("  CSC462 Lab 02 - All Tasks")
    print("=" * 45)
    for num, (title, _) in tasks.items():
        print(f"  {num}. {title}")
    print("  0. Exit")
    print("=" * 45)
    print("Note: Task 3 prints many lines (x from -pi to pi).")
    print("=" * 45)

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

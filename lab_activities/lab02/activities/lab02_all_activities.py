"""
CSC462 Lab 02 - All Solved Activities (1-6)
Run this file and choose an activity number from the menu.
"""

import math


def activity1_join_lists():
    """Accept two lists from user and display their join (concatenation)."""
    n1 = int(input("How many elements in first list? "))
    list1 = [int(input(f"  list1[{i}]: ")) for i in range(n1)]
    n2 = int(input("How many elements in second list? "))
    list2 = [int(input(f"  list2[{i}]: ")) for i in range(n2)]
    joined = list1 + list2
    print(f"List 1: {list1}")
    print(f"List 2: {list2}")
    print(f"Joined list: {joined}")


def activity2_palindrome():
    """Return True if string is palindrome (ignore case)."""

    def is_palindrome(s):
        cleaned = s.lower().replace(" ", "")
        return cleaned == cleaned[::-1]

    text = input("Enter a string: ")
    result = is_palindrome(text)
    print(f"'{text}' is a palindrome: {result}")


def activity3_matrix_multiply():
    """Find product C = a * b for two 3x3 matrices (2D lists)."""

    def read_matrix(name):
        print(f"Enter 3 rows for matrix {name} (3 space-separated numbers per row):")
        matrix = []
        for i in range(3):
            row = list(map(float, input(f"  row {i + 1}: ").split()))
            if len(row) != 3:
                raise ValueError("Each row must have exactly 3 numbers.")
            matrix.append(row)
        return matrix

    def multiply(a, b):
        rows, cols, inner = 3, 3, 3
        c = [[0] * cols for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                for k in range(inner):
                    c[i][j] += a[i][k] * b[k][j]
        return c

    use_sample = input("Use sample matrices from manual? (y/n): ").strip().lower()
    if use_sample == "y":
        a = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        b = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    else:
        a = read_matrix("a")
        b = read_matrix("b")

    c = multiply(a, b)
    print("Matrix a:")
    for row in a:
        print(row)
    print("Matrix b:")
    for row in b:
        print(row)
    print("Product C = a * b:")
    for row in c:
        print(row)


def activity4_polygon_perimeter():
    """Return perimeter of polygon from list of N (x, y) tuples."""

    def polygon_perimeter(points):
        n = len(points)
        if n < 2:
            return 0.0
        total = 0.0
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            total += math.hypot(x2 - x1, y2 - y1)
        return total

    use_sample = input("Use sample 6-sided polygon? (y/n): ").strip().lower()
    if use_sample == "y":
        # Sample 6-sided polygon (N=6)
        points = [(0, 0), (4, 0), (5, 2), (3, 4), (1, 4), (-1, 2)]
    else:
        n = int(input("Number of vertices N: "))
        points = []
        for i in range(n):
            x, y = map(float, input(f"  vertex {i + 1} (x y): ").split())
            points.append((x, y))

    perimeter = polygon_perimeter(points)
    print(f"Vertices: {points}")
    print(f"Perimeter: {perimeter:.4f}")


def activity5_symmetric_difference():
    """Symmetric difference without built-in set ops; compare with built-ins."""

    def symmetric_difference_manual(a, b):
        c = []
        for x in a:
            if x not in b and x not in c:
                c.append(x)
        for x in b:
            if x not in a and x not in c:
                c.append(x)
        return c

    print("Enter set A (space-separated numbers):")
    set_a = set(map(int, input().split()))
    print("Enter set B (space-separated numbers):")
    set_b = set(map(int, input().split()))

    manual = symmetric_difference_manual(list(set_a), list(set_b))
    builtin1 = set_a.symmetric_difference(set_b)
    builtin2 = set_b.symmetric_difference(set_a)
    builtin3 = set_a ^ set_b
    builtin4 = set_b ^ set_a

    print(f"Set A: {set_a}")
    print(f"Set B: {set_b}")
    print(f"Manual symmetric difference: {set(manual)}")
    print(f"A.symmetric_difference(B): {builtin1}")
    print(f"B.symmetric_difference(A): {builtin2}")
    print(f"A ^ B: {builtin3}")
    print(f"B ^ A: {builtin4}")


def activity6_phone_directory():
    """Dictionary with (first, last) tuple keys; search phone by name."""
    directory = {
        ("Ali", "Khan"): "0300-1111111",
        ("Sara", "Ahmed"): "0301-2222222",
        ("Usman", "Raza"): "0302-3333333",
    }

    print("Phone directory (initialized):")
    for name, number in directory.items():
        print(f"  {name[0]} {name[1]}: {number}")

    first = input("\nEnter first name to search: ").strip()
    last = input("Enter last name to search: ").strip()
    key = (first, last)

    if key in directory:
        print(f"Phone number: {directory[key]}")
    else:
        print("No matching phone number found.")


def main():
    activities = {
        1: ("Join Two Lists", activity1_join_lists),
        2: ("Palindrome Check", activity2_palindrome),
        3: ("Matrix Multiplication (3x3)", activity3_matrix_multiply),
        4: ("Polygon Perimeter", activity4_polygon_perimeter),
        5: ("Symmetric Difference of Sets", activity5_symmetric_difference),
        6: ("Phone Directory (Dictionary)", activity6_phone_directory),
    }

    print("=" * 45)
    print("  CSC462 Lab 02 - All Activities")
    print("=" * 45)
    for num, (title, _) in activities.items():
        print(f"  {num}. {title}")
    print("  0. Exit")
    print("=" * 45)

    choice = input("Select activity (1-6): ").strip()
    if choice == "0":
        return
    if choice.isdigit() and 1 <= int(choice) <= 6:
        print()
        activities[int(choice)][1]()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

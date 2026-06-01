"""
Activity 4: Accept 5 integers from user and display their sum.

Flowchart (before coding):
    START
      |
      v
    sum = 0, i = 1
      |
      v
    +------------------+
    | i <= 5 ?         |---NO---> print sum --> END
    +------------------+
      | YES
      v
    read integer, add to sum, i = i + 1
      |
      +---- (loop back)
"""

total = 0

for i in range(1, 6):
    value = int(input(f"Enter integer {i} of 5: "))
    total += value

print(f"Sum of 5 integers: {total}")

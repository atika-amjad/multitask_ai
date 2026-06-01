"""
CSC462 Lab 04 - All Graded Lab Tasks (1-2)
Task 1: DFS Arad → Bucharest (Romania map, Figure 14)
Task 2: Boggle — find valid words on 4×4 board (Figure 15)
"""

# --- Task 1: Romania DFS ------------------------------------------------------

ROMANIA_EDGES = [
    ("Arad", "Zerind", 75),
    ("Arad", "Sibiu", 140),
    ("Arad", "Timisoara", 118),
    ("Zerind", "Oradea", 71),
    ("Oradea", "Sibiu", 151),
    ("Sibiu", "Fagaras", 99),
    ("Sibiu", "Rimnicu Vilcea", 80),
    ("Timisoara", "Lugoj", 111),
    ("Lugoj", "Mehadia", 70),
    ("Mehadia", "Dobreta", 75),
    ("Dobreta", "Craiova", 120),
    ("Craiova", "Rimnicu Vilcea", 146),
    ("Craiova", "Pitesti", 138),
    ("Rimnicu Vilcea", "Pitesti", 97),
    ("Fagaras", "Bucharest", 211),
    ("Pitesti", "Bucharest", 101),
    ("Bucharest", "Giurgiu", 90),
    ("Bucharest", "Urziceni", 85),
    ("Urziceni", "Vaslui", 98),
    ("Urziceni", "Hirsova", 151),
    ("Hirsova", "Eforie", 161),
    ("Vaslui", "Iasi", 92),
    ("Iasi", "Neamt", 87),
]


def build_adjacency_from_edges(edges):
    adjacency = {}
    for city_a, city_b, _cost in edges:
        adjacency.setdefault(city_a, []).append(city_b)
        adjacency.setdefault(city_b, []).append(city_a)
    for city in adjacency:
        adjacency[city] = sorted(set(adjacency[city]))
    return adjacency


def dfs_graph(adjacency, start, goal):
    """DFS using stack (LIFO). Returns (path, explored_order)."""
    if start not in adjacency or goal not in adjacency:
        return None, []

    stack = [(start, [start])]
    visited = {start}
    explored = []

    while stack:
        state, path = stack.pop()
        explored.append(state)

        if state == goal:
            return path, explored

        for neighbor in adjacency[state]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))

    return None, explored


def task1_romania_dfs():
    """DFS from Arad to Bucharest (Figure 14)."""
    adjacency = build_adjacency_from_edges(ROMANIA_EDGES)
    start, goal = "Arad", "Bucharest"

    path, explored = dfs_graph(adjacency, start, goal)

    print("Romania Map (Figure 14) — Depth-First Search")
    print("-" * 50)
    print(f"Start: {start}")
    print(f"Goal:  {goal}")
    print(f"Explored order: {explored}")
    if path:
        print(f"\nPath ({len(path) - 1} segments):")
        print(" -> ".join(path))
        print("\nNote: DFS does not guarantee shortest distance; BFS gives fewer hops.")
    else:
        print("No path found.")


# --- Task 2: Boggle (DFS on board) --------------------------------------------

# Figure 15 — traditional 4×4 boggle board (Techie Delight / lab manual)
BOGGLE_BOARD = [
    ["M", "S", "E", "F"],
    ["R", "A", "T", "D"],
    ["L", "O", "N", "E"],
    ["K", "A", "F", "B"],
]

# Manual example dictionary and expected valid words
BOGGLE_DICTIONARY = ["START", "NOTE", "SAND", "STONED"]
EXPECTED_VALID = ["NOTE", "SAND", "STONED"]

# 8 directions: N, S, E, W, NE, NW, SE, SW
DIRECTIONS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
]


def is_safe(row, col, rows, cols, visited):
    return 0 <= row < rows and 0 <= col < cols and (row, col) not in visited


def can_form_word(board, word):
    """DFS: check if word exists on board (8 directions, no cell reuse)."""
    rows, cols = len(board), len(board[0])
    target = word.upper()

    def dfs(row, col, index, visited):
        if board[row][col] != target[index]:
            return False
        if index == len(target) - 1:
            return True

        visited.add((row, col))
        for dr, dc in DIRECTIONS:
            nr, nc = row + dr, col + dc
            if is_safe(nr, nc, rows, cols, visited):
                if dfs(nr, nc, index + 1, visited):
                    return True
        visited.remove((row, col))
        return False

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0, set()):
                return True
    return False


def find_valid_words(board, dictionary):
    """Return dictionary words that can be formed on the board."""
    return sorted([w for w in dictionary if can_form_word(board, w)])


def display_board(board, highlight=None):
    highlight = highlight or set()
    for r, row in enumerate(board):
        cells = []
        for c, ch in enumerate(row):
            cells.append(f"[{ch}]" if (r, c) in highlight else f" {ch} ")
        print(" ".join(cells))


def task2_boggle_words():
    """Find valid words from dictionary on boggle board (Figure 15)."""
    print("Boggle Board (Figure 15) — DFS word search")
    print("-" * 50)
    display_board(BOGGLE_BOARD)
    print(f"\nDictionary: {BOGGLE_DICTIONARY}")

    valid = find_valid_words(BOGGLE_BOARD, BOGGLE_DICTIONARY)

    print(f"\nValid words found: {valid}")
    print(f"Expected (manual): {EXPECTED_VALID}")
    print(f"Match: {valid == EXPECTED_VALID}")

    print("\nPer-word check:")
    for word in BOGGLE_DICTIONARY:
        ok = can_form_word(BOGGLE_BOARD, word)
        print(f"  {word}: {'YES' if ok else 'NO'}")


def main():
    tasks = {
        1: ("Romania: Arad → Bucharest (DFS)", task1_romania_dfs),
        2: ("Boggle Word Search (DFS)", task2_boggle_words),
    }

    print("=" * 45)
    print("  CSC462 Lab 04 - All Tasks")
    print("=" * 45)
    for num, (title, _) in tasks.items():
        print(f"  {num}. {title}")
    print("  0. Exit")
    print("=" * 45)

    choice = input("Select task (1-2): ").strip()
    if choice == "0":
        return
    if choice.isdigit() and 1 <= int(choice) <= 2:
        print()
        tasks[int(choice)][1]()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

"""
CSC462 Lab 03 - All Graded Lab Tasks (1-2)
Task 1: BFS Arad → Bucharest (Romania map, Figure 9)
Task 2: BFS maze escape (Figure 10 puzzle grid)
"""

from collections import deque


# --- Shared BFS helpers -------------------------------------------------------

def bfs_graph(adjacency, start, goal):
    """BFS on adjacency list; returns (path, explored_order)."""
    if start not in adjacency or goal not in adjacency:
        return None, []

    queue = deque([(start, [start])])
    visited = {start}
    explored = []

    while queue:
        state, path = queue.popleft()
        explored.append(state)

        if state == goal:
            return path, explored

        for neighbor in adjacency[state]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None, explored


def build_adjacency_from_edges(edges):
    """Build undirected adjacency list from (city1, city2, cost) tuples."""
    adjacency = {}
    for city_a, city_b, _cost in edges:
        adjacency.setdefault(city_a, []).append(city_b)
        adjacency.setdefault(city_b, []).append(city_a)
    for city in adjacency:
        adjacency[city] = sorted(set(adjacency[city]))
    return adjacency


# --- Task 1: Romania map ----------------------------------------------------

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


def task1_romania_bfs():
    """BFS from Arad to Bucharest on Romania road map."""
    adjacency = build_adjacency_from_edges(ROMANIA_EDGES)
    start, goal = "Arad", "Bucharest"

    path, explored = bfs_graph(adjacency, start, goal)

    print("Romania Map (Figure 9) — Breadth-First Search")
    print("-" * 50)
    print(f"Start: {start}")
    print(f"Goal:  {goal}")
    print(f"Explored order: {explored}")
    if path:
        print(f"\nPath ({len(path) - 1} road segments):")
        print(" -> ".join(path))
    else:
        print("No path found.")


# --- Task 2: Maze BFS ---------------------------------------------------------

# Figure 10 maze: 0 = open path, 1 = wall
MAZE = [
    [1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

MAZE_START = (3, 3)   # row, col — start position (Figure 10)
MAZE_EXIT = (0, 6)    # row, col — exit/opening at top


def bfs_maze(maze, start, goal):
    """BFS on grid; returns (path, explored_count)."""
    rows, cols = len(maze), len(maze[0])
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (row, col), path = queue.popleft()

        if (row, col) == goal:
            return path, len(visited)

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and maze[nr][nc] == 0
                and (nr, nc) not in visited
            ):
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

    return None, len(visited)


def moves_between(path):
    """Convert coordinate path to UP/DOWN/LEFT/RIGHT moves."""
    names = {(-1, 0): "UP", (1, 0): "DOWN", (0, -1): "LEFT", (0, 1): "RIGHT"}
    moves = []
    for i in range(1, len(path)):
        dr = path[i][0] - path[i - 1][0]
        dc = path[i][1] - path[i - 1][1]
        moves.append(names[(dr, dc)])
    return moves


def display_maze(maze, path=None):
    """Print maze; mark path with '*'."""
    path_set = set(path) if path else set()
    for r, row in enumerate(maze):
        line = []
        for c, cell in enumerate(row):
            if (r, c) in path_set:
                line.append("*")
            elif cell == 1:
                line.append("#")
            else:
                line.append(".")
        print("".join(line))


def task2_maze_bfs():
    """BFS to escape maze from start to exit (Figure 10)."""
    path, visited_count = bfs_maze(MAZE, MAZE_START, MAZE_EXIT)

    print("Maze Puzzle (Figure 10) — Breadth-First Search")
    print("-" * 50)
    print(f"Start (row, col): {MAZE_START}")
    print(f"Exit  (row, col): {MAZE_EXIT}")
    print(f"Cells explored: {visited_count}")

    if not path:
        print("No path found.")
        return

    moves = moves_between(path)
    print(f"\nPath length: {len(path) - 1} steps")
    print(f"Coordinates: {path}")
    print(f"Moves: {' -> '.join(moves)}")

    print("\nMaze with BFS path (* = route, # = wall, . = open):")
    display_maze(MAZE, path)


def main():
    tasks = {
        1: ("Romania: Arad → Bucharest (BFS)", task1_romania_bfs),
        2: ("Maze Escape (BFS)", task2_maze_bfs),
    }

    print("=" * 45)
    print("  CSC462 Lab 03 - All Tasks")
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

"""
CSC462 Lab 03 - Breadth First Search (All Activities)
Activity 1:   Represent state-space graph in Python
Activity 1-b: BFS path from start to goal (A→F, and D→C demo)
"""

from collections import deque


class Node:
    """Search node: state, parent, action, path_cost."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def __repr__(self):
        return f"Node({self.state}, cost={self.path_cost})"


def build_toy_graph():
    """
    Figure 8 toy graph (adjacency list).
    Neighbor order matters for BFS tie-breaking (matches manual solutions).
    """
    adjacency = {
        "A": ["C", "B", "E"],
        "B": ["A", "D"],
        "C": ["A", "F"],
        "D": ["B", "E"],
        "E": ["A", "D"],
        "F": ["C"],
    }
    graph = {}
    for state in adjacency:
        graph[state] = Node(state)
    return graph, adjacency


def action_sequence(node):
    """Reconstruct path from goal node back to start via parent pointers."""
    path = []
    current = node
    while current is not None:
        path.append(current.state)
        current = current.parent
    path.reverse()
    return path


def bfs(graph, adjacency, start, goal):
    """
    Breadth-first search on state-space graph.
    Returns (path, explored_order).
    """
    if start not in graph or goal not in graph:
        return None, []

    for state in graph:
        graph[state].parent = None
        graph[state].path_cost = 0

    start_node = graph[start]
    queue = deque([start_node])
    visited = {start}
    explored = []

    while queue:
        current = queue.popleft()
        explored.append(current.state)

        if current.state == goal:
            return action_sequence(current), explored

        for neighbor in adjacency[current.state]:
            if neighbor not in visited:
                visited.add(neighbor)
                child = graph[neighbor]
                child.parent = current
                child.path_cost = current.path_cost + 1
                child.action = f"{current.state} -> {neighbor}"
                queue.append(child)

    return None, explored


def activity1_graph_representation():
    """Activity 1: Represent the toy problem graph in Python."""
    graph, adjacency = build_toy_graph()

    print("State-space graph (dictionary of Node objects):")
    print("-" * 50)
    for state, node in graph.items():
        print(f"  {state}: {node}")
        print(f"       neighbors -> {adjacency[state]}")

    print("\nAdjacency list (used for BFS):")
    for state, neighbors in adjacency.items():
        print(f"  {state}: {neighbors}")

    print("\nNode attributes (per lab manual):")
    print("  1. state   2. parent   3. action   4. path_cost")


def activity1b_bfs_paths():
    """Activity 1-b: BFS from A to F; demo D to C (manual answers)."""
    graph, adjacency = build_toy_graph()

    demos = [
        ("A", "F", "Start A, goal F (main activity)", ["A", "C", "F"]),
        ("D", "C", "Start D, goal C (manual follow-up)", ["D", "B", "A", "C"]),
    ]

    for start, goal, label, expected in demos:
        print("=" * 50)
        print(label)
        print("=" * 50)
        path, explored = bfs(graph, adjacency, start, goal)
        print(f"BFS explored order: {explored}")
        if path:
            print(f"Path from {start} to {goal}: {path}")
            print(f"Expected (manual): {expected}")
            print(f"Match: {path == expected}")
            print(f"Actions: {' -> '.join(path)}")
        else:
            print("No path found.")
        print()


def activity1b_custom():
    """Let user try custom start/goal on the toy graph."""
    graph, adjacency = build_toy_graph()
    print(f"Available nodes: {list(adjacency.keys())}")
    start = input("Start node: ").strip().upper()
    goal = input("Goal node: ").strip().upper()
    path, explored = bfs(graph, adjacency, start, goal)
    print(f"Explored: {explored}")
    print(f"Path: {path}")


def main():
    activities = {
        1: ("Graph Representation (Activity 1)", activity1_graph_representation),
        2: ("BFS A→F and D→C (Activity 1-b)", activity1b_bfs_paths),
        3: ("Custom BFS on Toy Graph", activity1b_custom),
    }

    print("=" * 45)
    print("  CSC462 Lab 03 - BFS Activities")
    print("=" * 45)
    for num, (title, _) in activities.items():
        print(f"  {num}. {title}")
    print("  0. Exit")
    print("=" * 45)

    choice = input("Select activity (1-3): ").strip()
    if choice == "0":
        return
    if choice.isdigit() and 1 <= int(choice) <= 3:
        print()
        activities[int(choice)][1]()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

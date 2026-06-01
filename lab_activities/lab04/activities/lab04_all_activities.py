"""
CSC462 Lab 04 - Depth First Search (All Activities)
Activity 1:   Represent state-space graph in Python (Figure 13)
Activity 1-b: DFS from A to F (stack / LIFO)
Activity 2:   BFS from D to C — path and explored order (comparison)
Bonus:        Connected components using DFS
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
    """Figure 13 toy graph (same structure as Lab 03 Figure 8)."""
    adjacency = {
        "A": ["C", "B", "E"],
        "B": ["A", "D"],
        "C": ["A", "F"],
        "D": ["B", "E"],
        "E": ["A", "D"],
        "F": ["C"],
    }
    graph = {state: Node(state) for state in adjacency}
    return graph, adjacency


def action_sequence(node):
    """Reconstruct path from goal back to start."""
    path = []
    current = node
    while current is not None:
        path.append(current.state)
        current = current.parent
    path.reverse()
    return path


def dfs(graph, adjacency, start, goal):
    """
    Depth-first search using a stack (LIFO).
    Neighbors are pushed in list order; last pushed is explored first.
    """
    if start not in graph or goal not in graph:
        return None, []

    for state in graph:
        graph[state].parent = None
        graph[state].path_cost = 0

    start_node = graph[start]
    stack = [start_node]
    visited = {start}
    explored = []

    while stack:
        current = stack.pop()
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
                stack.append(child)

    return None, explored


def bfs(graph, adjacency, start, goal):
    """Breadth-first search (FIFO) for Activity 2 comparison."""
    if start not in graph or goal not in graph:
        return None, []

    for state in graph:
        graph[state].parent = None

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
                queue.append(child)

    return None, explored


def connected_components(adjacency):
    """Count connected components using DFS (Lab 04 useful concepts)."""
    visited = set()
    components = []

    for node in adjacency:
        if node not in visited:
            component = []
            stack = [node]
            visited.add(node)
            while stack:
                current = stack.pop()
                component.append(current)
                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)
            components.append(component)

    return components


def activity1_graph_representation():
    """Activity 1: Represent graph using Node dictionary + adjacency list."""
    graph, adjacency = build_toy_graph()

    print("Figure 13 — State-space graph in Python")
    print("-" * 50)
    for state, node in graph.items():
        print(f"  {state}: {node}")
        print(f"       neighbors -> {adjacency[state]}")

    print("\nDFS vs BFS:")
    print("  BFS uses a queue (FIFO) — explores layer by layer")
    print("  DFS uses a stack (LIFO) — explores one branch deeply first")


def activity1b_dfs_a_to_f():
    """Activity 1-b: DFS from A to goal F."""
    graph, adjacency = build_toy_graph()
    start, goal = "A", "F"

    path, explored = dfs(graph, adjacency, start, goal)

    print("DFS: Start A, Goal F")
    print("-" * 50)
    print(f"Explored order: {explored}")
    print(f"First three explored: {explored[:3]}  (manual prefix: A, E, D)")
    if path:
        print(f"Path to goal F: {path}")
        print(f"Actions: {' -> '.join(path)}")
    else:
        print("No path found.")

    # Manual typo note: PDF shows ['A','E','D'] which is path to D, not F
    graph2, adj2 = build_toy_graph()
    path_d, _ = dfs(graph2, adj2, "A", "D")
    print(f"\nManual lists ['A','E','D'] — matches DFS path to D: {path_d}")


def activity2_bfs_d_to_c():
    """Activity 2: BFS from D to C (path + explored sequence)."""
    graph, adjacency = build_toy_graph()
    start, goal = "D", "C"

    path, explored = bfs(graph, adjacency, start, goal)

    print("BFS: Start D, Goal C (Activity 2)")
    print("-" * 50)
    print(f"Explored order: {explored}")
    print(f"Expanded before goal (manual): D, E, A")
    if path:
        print(f"Path: {path}")
        print(f"Expected (manual): ['D', 'B', 'A', 'C']")
        print(f"Match: {path == ['D', 'B', 'A', 'C']}")
    else:
        print("No path found.")


def activity_connected_components():
    """Demo: connected components (Figure 12 style example)."""
    # Example from manual: 3 components {1,2,3}, {4,5}, {6}
    example = {
        "1": ["2"],
        "2": ["1", "3"],
        "3": ["2"],
        "4": ["5"],
        "5": ["4"],
        "6": [],
    }
    components = connected_components(example)

    print("Connected Components (DFS demo)")
    print("-" * 50)
    print(f"Graph: {example}")
    for i, comp in enumerate(components, 1):
        print(f"  Component {i}: {sorted(comp)}")
    print(f"Number of connected components: {len(components)}")
    print("Expected (manual example): 3")


def activity_custom_dfs():
    """Custom start/goal DFS on toy graph."""
    graph, adjacency = build_toy_graph()
    print(f"Nodes: {list(adjacency.keys())}")
    start = input("Start: ").strip().upper()
    goal = input("Goal: ").strip().upper()
    path, explored = dfs(graph, adjacency, start, goal)
    print(f"Explored: {explored}")
    print(f"Path: {path}")


def main():
    activities = {
        1: ("Graph Representation (Activity 1)", activity1_graph_representation),
        2: ("DFS A → F (Activity 1-b)", activity1b_dfs_a_to_f),
        3: ("BFS D → C (Activity 2)", activity2_bfs_d_to_c),
        4: ("Connected Components (DFS demo)", activity_connected_components),
        5: ("Custom DFS on Toy Graph", activity_custom_dfs),
    }

    print("=" * 45)
    print("  CSC462 Lab 04 - DFS Activities")
    print("=" * 45)
    for num, (title, _) in activities.items():
        print(f"  {num}. {title}")
    print("  0. Exit")
    print("=" * 45)

    choice = input("Select activity (1-5): ").strip()
    if choice == "0":
        return
    if choice.isdigit() and 1 <= int(choice) <= 5:
        print()
        activities[int(choice)][1]()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

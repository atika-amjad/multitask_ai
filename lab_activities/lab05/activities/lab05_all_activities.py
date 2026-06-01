"""
CSC462 Lab 05 - Iterative Deepening Search (All Activities)
Activity 1:   Graph representation (Figure 17)
Activity 2:   IDS on Figure 16 tree (depth 0 → 1 → 2 …)
Activity 3:   IDS on toy graph (A→F, D→C)
Activity 4:   Compare IDS / BFS / DFS on same graph
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
    """Figure 17 toy graph (same as Lab 03/04)."""
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


def build_figure16_tree():
    """Figure 16 — IDS example tree (node 0 to goal node 6)."""
    return {
        "0": ["1", "2"],
        "1": ["3", "4"],
        "2": ["5", "6"],
        "3": [],
        "4": [],
        "5": [],
        "6": [],
    }


def reconstruct_path(goal_node):
    path = []
    current = goal_node
    while current is not None:
        path.append(current.state)
        current = current.parent
    path.reverse()
    return path


def depth_limited_search(graph, adjacency, start, goal, limit):
    """
    DFS with depth limit; no global visited (re-explores nodes at deeper iterations).
    Cycle avoidance: do not repeat a state on the current path.
    Returns (goal_node or None, explored_order for this depth limit).
    """
    explored = []

    def dls(current, depth, on_path):
        explored.append(current.state)
        if current.state == goal:
            return current
        if depth == 0:
            return None

        for neighbor in adjacency[current.state]:
            if neighbor in on_path:
                continue
            child = graph[neighbor]
            child.parent = current
            child.path_cost = current.path_cost + 1
            result = dls(child, depth - 1, on_path | {neighbor})
            if result is not None:
                return result
        return None

    for state in graph:
        graph[state].parent = None
        graph[state].path_cost = 0

    return dls(graph[start], limit, {start}), explored


def iterative_deepening(graph, adjacency, start, goal, max_depth=20):
    """
    IDS: increase depth limit until goal is found.
    Returns (path, depth_limit_used, list of explored orders per iteration).
    """
    all_iterations = []
    for depth in range(max_depth + 1):
        goal_node, explored = depth_limited_search(graph, adjacency, start, goal, depth)
        all_iterations.append((depth, explored))
        if goal_node is not None:
            return reconstruct_path(goal_node), depth, all_iterations
    return None, None, all_iterations


def bfs(graph, adjacency, start, goal):
    for state in graph:
        graph[state].parent = None
    queue = deque([graph[start]])
    visited = {start}
    while queue:
        current = queue.popleft()
        if current.state == goal:
            return reconstruct_path(current)
        for neighbor in adjacency[current.state]:
            if neighbor not in visited:
                visited.add(neighbor)
                child = graph[neighbor]
                child.parent = current
                queue.append(child)
    return None


def dfs(graph, adjacency, start, goal):
    for state in graph:
        graph[state].parent = None
    stack = [graph[start]]
    visited = {start}
    while stack:
        current = stack.pop()
        if current.state == goal:
            return reconstruct_path(current)
        for neighbor in adjacency[current.state]:
            if neighbor not in visited:
                visited.add(neighbor)
                child = graph[neighbor]
                child.parent = current
                stack.append(child)
    return None


def activity1_graph_representation():
    """Activity 1: Represent state-space graph for IDS."""
    graph, adjacency = build_toy_graph()

    print("Figure 17 — State-space graph in Python")
    print("-" * 50)
    for state, node in graph.items():
        print(f"  {state}: {node}  ->  {adjacency[state]}")

    print("\nIterative Deepening Search (IDS):")
    print("  • Run depth-limited DFS with limit = 0, 1, 2, …")
    print("  • Stop when goal is found")
    print("  • Optimal path length on unweighted graphs (like BFS)")
    print("  • Space: O(d) — much less than BFS frontier")


def activity2_figure16_ids_demo():
    """Activity 2: IDS on Figure 16 tree (start 0, goal 6)."""
    adjacency = build_figure16_tree()
    graph = {s: Node(s) for s in adjacency}
    start, goal = "0", "6"

    print("Figure 16 — IDS step-by-step (start 0, goal 6)")
    print("-" * 50)

    path, depth_used, iterations = iterative_deepening(graph, adjacency, start, goal)

    for limit, explored in iterations:
        found = goal in explored and (limit == depth_used)
        print(f"  Depth limit {limit}: explored {explored}" + ("  -> goal found" if found else ""))

    print(f"\nGoal found at depth limit: {depth_used}")
    print(f"Path: {path}")
    print("Expected path (manual): ['0', '2', '6']")


def activity3_ids_toy_graph():
    """Activity 3: IDS on toy graph — A→F and D→C."""
    graph, adjacency = build_toy_graph()

    demos = [
        ("A", "F", ["A", "C", "F"]),
        ("D", "C", ["D", "B", "A", "C"]),
    ]

    for start, goal, expected in demos:
        print("=" * 50)
        print(f"IDS: {start} -> {goal}")
        print("=" * 50)
        path, depth, iterations = iterative_deepening(graph, adjacency, start, goal)
        print(f"Depth limit when found: {depth}")
        print(f"Path: {path}")
        print(f"Expected: {expected}")
        print(f"Match: {path == expected}")
        print(f"Iterations: {len(iterations)}")
        print()


def activity4_compare_algorithms():
    """Compare IDS, BFS, and DFS on A → F."""
    graph, adjacency = build_toy_graph()
    start, goal = "A", "F"

    g1, a1 = build_toy_graph()
    g2, a2 = build_toy_graph()
    g3, a3 = build_toy_graph()

    ids_path, ids_depth, _ = iterative_deepening(g1, a1, start, goal)
    bfs_path = bfs(g2, a2, start, goal)
    dfs_path = dfs(g3, a3, start, goal)

    print("Algorithm comparison: A → F")
    print("-" * 50)
    print(f"  IDS (depth {ids_depth}): {ids_path}")
    print(f"  BFS:                   {bfs_path}")
    print(f"  DFS:                   {dfs_path}")
    print("\nIDS and BFS both find shortest path on unweighted graph.")


def activity_custom_ids():
    """Custom start/goal IDS on toy graph."""
    graph, adjacency = build_toy_graph()
    print(f"Nodes: {list(adjacency.keys())}")
    start = input("Start: ").strip().upper()
    goal = input("Goal: ").strip().upper()
    path, depth, _ = iterative_deepening(graph, adjacency, start, goal)
    print(f"Path: {path}  (found at depth limit {depth})")


def main():
    activities = {
        1: ("Graph Representation (Activity 1)", activity1_graph_representation),
        2: ("IDS on Figure 16 Tree", activity2_figure16_ids_demo),
        3: ("IDS A→F and D→C (Toy Graph)", activity3_ids_toy_graph),
        4: ("Compare IDS / BFS / DFS", activity4_compare_algorithms),
        5: ("Custom IDS", activity_custom_ids),
    }

    print("=" * 45)
    print("  CSC462 Lab 05 - IDS Activities")
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

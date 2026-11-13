"""OR-Tools' knapsack example, solved by OR-Tools' knapsack solver and by this module's search."""
# Adapted from the OR-Tools example knapsack.py, https://github.com/google/or-tools/blob/stable/ortools/algorithms/samples/knapsack.py

from ortools.algorithms.python import knapsack_solver

from gridcap import generate
from knapsack import Item, gridcap_knapsack, solve

VALUES = [
    360, 83, 59, 130, 431, 67, 230, 52, 93, 125, 670, 892, 600, 38, 48, 147, 78, 256, 63, 17, 120,
    164, 432, 35, 92, 110, 22, 42, 50, 323, 514, 28, 87, 73, 78, 15, 26, 78, 210, 36, 85, 189, 274,
    43, 33, 10, 19, 389, 276, 312,
]
WEIGHTS = [
    7, 0, 30, 22, 80, 94, 11, 81, 70, 64, 59, 18, 0, 36, 3, 8, 15, 42, 9, 0, 42, 47, 52, 32, 26, 48,
    55, 6, 29, 84, 2, 4, 18, 56, 7, 29, 93, 44, 71, 3, 86, 66, 31, 65, 0, 79, 20, 65, 52, 13,
]
CAPACITY = 850


def ortools_solve(values: list[int], weights: list[int], capacity: int) -> tuple[int, list[int]]:
    """OR-Tools' own knapsack solver, in its branch-and-bound mode: the best value and the items packed."""
    solver = knapsack_solver.KnapsackSolver(
        knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "knapsack")
    solver.init(values, [weights], [capacity])
    value = solver.solve()
    return value, [i for i in range(len(values)) if solver.best_solution_contains(i)]


if __name__ == "__main__":
    value, packed = ortools_solve(VALUES, WEIGHTS, CAPACITY)
    print(f"OR-Tools example, {len(VALUES)} items, capacity {CAPACITY}")
    print(f"  KnapsackSolver: value {value:,}, weight {sum(WEIGHTS[i] for i in packed)}, {len(packed)} items packed")
    free = [i for i, w in enumerate(WEIGHTS) if w == 0]                 # our search needs every cost > 0
    items = [Item(f"i{i:02}", v, w) for i, (v, w) in enumerate(zip(VALUES, WEIGHTS)) if w > 0]
    ours = solve(items, CAPACITY)
    taken_free = sum(VALUES[i] for i in free)
    print(f"  our search:     value {taken_free:,} from the {len(free)} items of weight 0"
          f" + {ours.value:,} = {taken_free + ours.value:,}, in {ours.nodes} nodes")

    items, budget, _ = gridcap_knapsack(generate("small"))
    value, packed = ortools_solve([it.value for it in items], [it.cost for it in items], budget)
    print(f"GridCap small, {len(items)} projects, budget left {budget:,}")
    print(f"  KnapsackSolver: value {value:,}, {len(packed)} projects funded")

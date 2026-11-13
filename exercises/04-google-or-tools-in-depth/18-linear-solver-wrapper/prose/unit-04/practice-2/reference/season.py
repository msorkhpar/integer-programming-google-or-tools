from __future__ import annotations

from ortools.algorithms.python import knapsack_solver

SCALE = 100         # months are given to two decimal places


def best_season(values: list[int], months: list[float], season: float) -> tuple[int, list[int]]:
    """The most valuable set of jobs whose crew-months fit in one season: (value, sorted job indices)."""
    weights = [[round(m * SCALE) for m in months]]
    capacity = [round(season * SCALE)]
    solver = knapsack_solver.KnapsackSolver(
        knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "season")
    solver.init(values, weights, capacity)
    best = solver.solve()
    return best, [i for i in range(len(values)) if solver.best_solution_contains(i)]


if __name__ == "__main__":
    print(best_season([5, 6, 4], [2.5, 3.0, 4.5], 6.0))

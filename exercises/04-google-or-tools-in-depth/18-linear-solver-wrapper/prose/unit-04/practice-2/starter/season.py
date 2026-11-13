from __future__ import annotations

from ortools.algorithms.python import knapsack_solver

SCALE = 100         # months are given to two decimal places


def best_season(values: list[int], months: list[float], season: float) -> tuple[int, list[int]]:
    """The most valuable set of jobs whose crew-months fit in one season: (value, sorted job indices)."""
    # TODO: whole-number data for KnapsackSolver, then solve and read the chosen jobs.
    return 0, []


if __name__ == "__main__":
    print(best_season([5, 6, 4], [2.5, 3.0, 4.5], 6.0))

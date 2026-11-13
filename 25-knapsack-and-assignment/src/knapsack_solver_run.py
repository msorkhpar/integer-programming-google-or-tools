"""Lesson 6.3.1: OR-Tools' own knapsack solver on GridCap small, with one row and with six.

Adapted from the OR-Tools example `ortools/algorithms/samples/knapsack.py` (Apache-2.0): the same
`KnapsackSolver` calls, with GridCap's projects as the items. GridCap is a fictional utility's portfolio.
"""
# Adapted from the OR-Tools example knapsack.py, https://github.com/google/or-tools/blob/stable/ortools/algorithms/samples/knapsack.py

from ortools.algorithms.python import knapsack_solver

from gridcap import generate
from knapsack_models import capital_row, discretionary, year_rows

small = generate("small")
projects = discretionary(small)
values = [p.value for p in projects]
all_rows = [capital_row(small)] + year_rows(small)

for rows in (all_rows[:1], all_rows):
    weights = [[row.weight.get(p.project_id, 0) for p in projects] for row in rows]   # one list per row
    capacities = [row.capacity for row in rows]
    solver = knapsack_solver.KnapsackSolver(
        knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "GridCapSmall")
    solver.init(values, weights, capacities)
    best = solver.solve()
    packed = [p.project_id for k, p in enumerate(projects) if solver.best_solution_contains(k)]
    print(f"{len(rows)} row(s): value ${best:,}k, {len(packed)} projects")

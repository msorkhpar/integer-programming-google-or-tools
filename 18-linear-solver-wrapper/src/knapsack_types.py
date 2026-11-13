"""Lesson 4.7.4: KnapsackSolver on the OR-Tools 50-item example, with each of its solver types.

Adapted from the OR-Tools example knapsack.py,
https://github.com/google/or-tools/blob/stable/ortools/algorithms/samples/knapsack.py (Apache-2.0).
Every type is run on the example's one row and on two rows, each run in a child process, because
the solver stops the whole process when it is given data its type cannot handle.
"""

import re
import subprocess
import sys

from ortools.algorithms.python import knapsack_solver

VALUES = [360, 83, 59, 130, 431, 67, 230, 52, 93, 125, 670, 892, 600, 38, 48, 147, 78, 256, 63, 17, 120,
          164, 432, 35, 92, 110, 22, 42, 50, 323, 514, 28, 87, 73, 78, 15, 26, 78, 210, 36, 85, 189, 274,
          43, 33, 10, 19, 389, 276, 312]
WEIGHTS = [[7, 0, 30, 22, 80, 94, 11, 81, 70, 64, 59, 18, 0, 36, 3, 8, 15, 42, 9, 0, 42, 47, 52, 32, 26,
            48, 55, 6, 29, 84, 2, 4, 18, 56, 7, 29, 93, 44, 71, 3, 86, 66, 31, 65, 0, 79, 20, 65, 52, 13]]
CAPACITIES = [850]
ONE_ROW = ("KNAPSACK_BRUTE_FORCE_SOLVER", "KNAPSACK_64ITEMS_SOLVER", "KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER",
           "KNAPSACK_DIVIDE_AND_CONQUER_SOLVER")
ANY_ROWS = ("KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER", "KNAPSACK_MULTIDIMENSION_CBC_MIP_SOLVER",
            "KNAPSACK_MULTIDIMENSION_SCIP_MIP_SOLVER", "KNAPSACK_MULTIDIMENSION_CP_SAT_SOLVER")


def solve(type_name: str, values, weights, capacities) -> tuple[int, list[int]]:
    solver = knapsack_solver.KnapsackSolver(getattr(knapsack_solver.SolverType, type_name), "example")
    solver.init(values, weights, capacities)
    best = solver.solve()
    return best, [i for i in range(len(values)) if solver.best_solution_contains(i)]


REASONS: dict[str, str] = {}                # aborted run -> the solver's own message


def run_in_child(type_name: str, rows: int) -> str:
    child = subprocess.run([sys.executable, __file__, type_name, str(rows)], capture_output=True, text=True)
    if child.returncode == 0:
        return f"value {child.stdout.strip()}"
    found = re.findall(r"Check failed: (.*)", child.stderr)
    REASONS[f"{type_name.removeprefix('KNAPSACK_')}, {rows} row{'s' if rows > 1 else ''}"] = found[0] if found else "(none)"
    return f"process stopped, exit code {child.returncode}"


if len(sys.argv) > 1:                       # the child process: one solve, with one row or with two
    rows = int(sys.argv[2])
    weights, capacities = (WEIGHTS, CAPACITIES) if rows == 1 else (WEIGHTS + [[1] * len(VALUES)], CAPACITIES + [30])
    print(solve(sys.argv[1], VALUES, weights, capacities)[0])
    sys.exit(0)

best, packed = solve("KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER", VALUES, WEIGHTS, CAPACITIES)
print(f"total value = {best}, total weight = {sum(WEIGHTS[0][i] for i in packed)}, {len(packed)} items packed")
print(f"{'solver type':48} {'one row: weight <= 850':32} two rows: and at most 30 items")
for name in ONE_ROW + ANY_ROWS:
    print(f"{name:48} {run_in_child(name, 1):32} {run_in_child(name, 2)}")
print("the solver's message for each stopped run:")
for run, reason in REASONS.items():
    print(f"  {run}: {reason}")

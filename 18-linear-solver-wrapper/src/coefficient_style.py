"""Lesson 4.7.1: rows and an objective built coefficient by coefficient, then read back as LP text.

Adapted from the OR-Tools example mip_var_array.py,
https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/mip_var_array.py
(Apache-2.0): its data and its `RowConstraint` / `SetCoefficient` style.
"""

from ortools.linear_solver import pywraplp

COEFFS = [[5, 7, 9, 2, 1], [18, 4, -9, 10, 12], [4, 7, 3, 8, 5], [5, 13, 16, 3, -7]]
BOUNDS = [250, 285, 211, 315]
OBJ = [7, 8, 2, 9, 6]

solver = pywraplp.Solver.CreateSolver("SCIP")
infinity = solver.infinity()
x = [solver.IntVar(0, infinity, f"x{j}") for j in range(len(OBJ))]

for i, row in enumerate(COEFFS):
    constraint = solver.RowConstraint(0, BOUNDS[i], f"row{i}")     # 0 <= ... <= BOUNDS[i]
    for j, a in enumerate(row):
        constraint.SetCoefficient(x[j], a)

objective = solver.Objective()
for j, c in enumerate(OBJ):
    objective.SetCoefficient(x[j], c)
objective.SetMaximization()

print(solver.ExportModelAsLpFormat(False))
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(f"objective = {objective.Value():.0f}")
    print("  " + ", ".join(f"{v.name()} = {v.solution_value():.0f}" for v in x))
    for c in solver.constraints():
        activity = sum(c.GetCoefficient(v) * v.solution_value() for v in x)
        print(f"  {c.name()}: {c.lb():.0f} <= {activity:.0f} <= {c.ub():.0f}")

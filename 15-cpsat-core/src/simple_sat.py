"""Lesson 4.4.1: the smallest CP-SAT program, three integer variables and one constraint.

Adapted from the OR-Tools example simple_sat_program.py,
https://github.com/google/or-tools/blob/stable/ortools/sat/samples/simple_sat_program.py (Apache-2.0).
"""

from ortools.sat.python import cp_model

model = cp_model.CpModel()

num_vals = 3
x = model.new_int_var(0, num_vals - 1, "x")
y = model.new_int_var(0, num_vals - 1, "y")
z = model.new_int_var(0, num_vals - 1, "z")

model.add(x != y)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"status {solver.status_name(status)}: x = {solver.value(x)}, y = {solver.value(y)}, z = {solver.value(z)}")
else:
    print("No solution found.")

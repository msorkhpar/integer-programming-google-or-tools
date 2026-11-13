"""Lesson 4.4.3: a row with a fraction, multiplied by 2 so every coefficient is a whole number.

Adapted from the OR-Tools example cp_sat_example.py ("Solving an Optimization Problem"),
https://github.com/google/or-tools/blob/stable/ortools/sat/samples/cp_sat_example.py (Apache-2.0).
The first row was x + 7/2 y + 3/2 z <= 25.
"""

from ortools.sat.python import cp_model

model = cp_model.CpModel()
var_upper_bound = max(50, 45, 37)
x = model.new_int_var(0, var_upper_bound, "x")
y = model.new_int_var(0, var_upper_bound, "y")
z = model.new_int_var(0, var_upper_bound, "z")

model.add(2 * x + 7 * y + 3 * z <= 50)          # x + 3.5 y + 1.5 z <= 25, times 2
model.add(3 * x - 5 * y + 7 * z <= 45)
model.add(5 * x + 2 * y - 6 * z <= 37)
model.maximize(2 * x + 2 * y + 3 * z)

solver = cp_model.CpSolver()
status = solver.solve(model)
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"{solver.status_name(status)}: objective {solver.objective_value:g}, "
          f"x = {solver.value(x)}, y = {solver.value(y)}, z = {solver.value(z)}")

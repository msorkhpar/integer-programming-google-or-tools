"""Lesson 4.4.1: linear constraints in CP-SAT take whole-number coefficients and bounds."""

from ortools.sat.python import cp_model

model = cp_model.CpModel()
a = model.new_bool_var("a")
b = model.new_bool_var("b")
crews = model.new_int_var(0, 10, "crews")

model.add(3 * a + 2 * b <= crews)                             # an inequality
model.add(a + b == 1)                                         # an equality
model.add_linear_constraint(2 * crews - a, 3, 7)              # a range: 3 <= 2 crews - a <= 7
model.add(crews != 3)                                         # "not equal" is allowed too

try:
    model.add(2.5 * a <= crews)
except TypeError as error:
    print("TypeError:", str(error).splitlines()[0])

model.maximize(crews)
solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status), {v.name: solver.value(v) for v in (a, b, crews)})

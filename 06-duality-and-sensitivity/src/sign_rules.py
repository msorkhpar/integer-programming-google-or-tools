"""Lesson 2.3.1: a >= row gets a price <= 0. The one-year LP with vegetation and a vegetation floor."""

from ortools.math_opt.python import mathopt

from budget_lp import clean, value_per_k, work_per_crew_month
from dualize import dualize
from gridcap import generate

tiny = generate("tiny")
YEAR, FLOOR = 2027, 300
v, k = value_per_k(tiny), work_per_crew_month(tiny)

model = mathopt.Model(name="one-year with floor")
x = {g: model.add_variable(lb=0, name=g[0]) for g in ("distribution", "transmission", "vegetation")}
model.add_linear_constraint(sum(x.values()) <= tiny.budget[YEAR], name="budget")
for g, var in x.items():
    model.add_linear_constraint(var <= k[g] * tiny.crews[g, YEAR], name=f"crew_{g[0]}")
model.add_linear_constraint(x["vegetation"] >= FLOOR, name="veg_floor")
model.maximize(sum(v[g] * var for g, var in x.items()))

primal = mathopt.solve(model, mathopt.SolverType.GLOP)
print(f"primal: value {primal.objective_value():,.1f}, plan",
      {var.name: round(primal.variable_values(var), 1) for var in x.values()})

dual_model, price = dualize(model)
dual = mathopt.solve(dual_model, mathopt.SolverType.GLOP)
print(f"dual:   value {dual.objective_value():,.1f}")
print(f"{'row':10} {'dual LP price':>14} {'MathOpt dual_values':>20}")
for row in model.linear_constraints():
    print(f"{row.name:10} {clean(dual.variable_values(price[row.name])):>14} {clean(primal.dual_values(row)):>20}")

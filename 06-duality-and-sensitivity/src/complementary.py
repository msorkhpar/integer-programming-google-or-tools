"""Lesson 2.3.2: at the optimum, slack times price is 0 on every row, value times reduced cost on every variable."""

from budget_lp import build, clean, solve_glop
from certificates import reduced_cost, slack
from gridcap import generate

tiny = generate("tiny")
lp = build(tiny)
result = solve_glop(lp.model)
plan = {var.name: result.variable_values(var) for var in lp.model.variables()}
prices = {row.name: result.dual_values(row) for row in lp.model.linear_constraints()}

print(f"{'row':26} {'slack':>8} {'price':>8} {'product':>8}")
for row in lp.model.linear_constraints():
    s, y = slack(row, plan), prices[row.name]
    print(f"{row.name:26} {clean(s, 1):>8} {clean(y):>8} {clean(s * y):>8}")
print()
print(f"{'variable':26} {'value':>8} {'red.cost':>8} {'product':>8}")
for var in lp.model.variables():
    x, d = plan[var.name], reduced_cost(lp.model, var, prices)
    print(f"{var.name:26} {clean(x, 1):>8} {clean(d):>8} {clean(x * d):>8}")

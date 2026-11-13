"""Lesson 2.3.2: certify a plan without a solver. Complementary slackness gives the prices; check their signs."""

import numpy as np

from budget_lp import build, clean, solve_glop
from certificates import TOL, plan_value, prices_are_feasible, reduced_cost, rhs, slack
from gridcap import generate

tiny = generate("tiny")
lp = build(tiny)
model = lp.model


def prices_from_plan(plan: dict[str, float]) -> dict[str, float]:
    """Price 0 on every row with slack; solve 'reduced cost = 0' for every variable the plan uses."""
    rows = [row for row in model.linear_constraints() if abs(slack(row, plan)) <= TOL]     # binding rows
    used = [var for var in model.variables() if plan[var.name] > TOL]                       # positive variables
    A = np.array([[row.get_coefficient(var) for row in rows] for var in used])              # one equation per variable
    c = np.array([model.objective.get_linear_coefficient(var) for var in used])
    y = np.linalg.solve(A, c)                                                               # needs as many of each
    prices = {row.name: 0.0 for row in model.linear_constraints()}
    prices.update({row.name: float(p) for row, p in zip(rows, y)})
    return prices


def report(name: str, plan: dict[str, float]) -> None:
    prices = prices_from_plan(plan)
    print(f"{name}: value {plan_value(model, plan):,.2f}, prices dual feasible: {prices_are_feasible(model, prices)}")
    for row in model.linear_constraints():
        y = prices[row.name]
        wrong_sign = (y < -TOL) if row.lower_bound == -float("inf") else (y > TOL)
        if wrong_sign:
            print(f"  {row.name}: price {clean(y)} has the wrong sign for a {'<=' if y < 0 else '>='} row")
    for var in model.variables():
        d = reduced_cost(model, var, prices)
        if d > TOL:
            print(f"  {var.name}: reduced cost {clean(d)} > 0, so more of it would pay")


solver_plan = solve_glop(model)
report("solver's plan", {var.name: solver_plan.variable_values(var) for var in model.variables()})

worse = {var.name: 0.0 for var in model.variables()}
worse.update({lp.spend[key].name: amount for key, amount in {
    ("distribution", 2027): 880, ("vegetation", 2027): 680, ("transmission", 2027): 740,
    ("distribution", 2028): 2640, ("vegetation", 2028): 220, ("transmission", 2028): 420,
    ("distribution", 2029): 1320, ("transmission", 2029): 990}.items()})
report("floor met early", worse)

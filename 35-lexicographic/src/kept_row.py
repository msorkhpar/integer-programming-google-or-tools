"""Why the kept row gets a small numerical slack: the solver's reported best can sit above its own plan."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from lex_model import build, solve

sm = build(generate("small"))
risk = sm.objective("risk")
sm.model.set_linear_objective(risk, is_maximize=True)
result = solve(sm.model, 0.0)                                   # pass 1: the most risk removed
best = result.objective_value()
own = mathopt.evaluate_expression(risk, result.variable_values())
print(f"pass 1 reports best risk removed {best!r}")
print(f"pass 1's own plan removes        {own!r}")
print(f"the plan sits {best - own:.1e} below best, so the row risk >= best excludes it by that much")

row = sm.model.add_linear_constraint(risk >= best, name="keep_risk")     # the exact row, no slack
sm.model.set_linear_objective(sm.objective("npv"), is_maximize=True)
second = solve(sm.model, 0.0)                                   # pass 2: the most NPV at that risk
print(f"pass 2 with the exact row: {second.termination.reason.name}")
sm.model.delete_linear_constraint(row)

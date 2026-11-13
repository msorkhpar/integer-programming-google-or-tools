"""Lesson 2.3.3: read shadow prices and reduced costs from MathOpt, with two LP solvers."""

from ortools.math_opt.python import mathopt

from budget_lp import build, clean
from gridcap import generate

tiny = generate("tiny")
lp = build(tiny)
glop = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
highs = mathopt.solve(lp.model, mathopt.SolverType.HIGHS)
for result in (glop, highs):
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(result.termination.reason.name)

print(f"{'row':24} {'GLOP':>8} {'HiGHS':>8}")
for y in tiny.years:
    for row in (lp.cash[y], lp.crew["distribution", y], lp.crew["vegetation", y]):
        print(f"{row.name:24} {clean(glop.dual_values(row)):>8} {clean(highs.dual_values(row)):>8}")
print(f"{lp.floor.name:24} {clean(glop.dual_values(lp.floor)):>8} {clean(highs.dual_values(lp.floor)):>8}")
print()
print(f"{'variable':24} {'value':>8} {'reduced cost':>13}")
for var in (lp.spend["vegetation", 2027], lp.spend["transmission", 2028], lp.carry[2027], lp.carry[2028]):
    print(f"{var.name:24} {clean(glop.variable_values(var), 1):>8} {clean(glop.reduced_costs(var)):>13}")
print()
# The same LP written as a minimization of -value: MathOpt's prices are the change in *that* objective.
as_min = build(tiny)
as_min.model.minimize(-as_min.model.objective.as_linear_expression())
flipped = mathopt.solve(as_min.model, mathopt.SolverType.GLOP)
print(f"min -value: objective {flipped.objective_value():,.1f}, {as_min.cash[2027].name} price "
      f"{clean(flipped.dual_values(as_min.cash[2027]))}, {as_min.floor.name} price {clean(flipped.dual_values(as_min.floor))}")

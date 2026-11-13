"""CP-SAT on a model with continuous variables: it answers, says OPTIMAL, and answers a different model."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve

S = mathopt.SolverType
lp = build(generate("small"), integer=False)          # every x[i] continuous in [0, 1]
for solver in (S.GLOP, S.HIGHS, S.CP_SAT):
    result = solve(lp.model, solver)
    fractional = sum(1 for v in lp.x.values() if 1e-6 < result.variable_values(v) < 1 - 1e-6)
    print(f"{solver.name:<6} {result.termination.reason.name} {result.objective_value():,.1f}"
          f"  fractional x: {fractional}")

model = mathopt.Model(name="one-continuous")
a = model.add_variable(lb=0, ub=10, name="a")              # continuous
b = model.add_integer_variable(lb=0, ub=10, name="b")
model.add_linear_constraint(0.37 * a + 1.13 * b <= 7.71, name="cap")
model.maximize(1.01 * a + 2.9 * b)
for solver in (S.HIGHS, S.CP_SAT):
    result = solve(model, solver)
    print(f"{solver.name:<6} {result.termination.reason.name} {result.objective_value():.4f}"
          f"  a = {result.variable_values(a):.4f}  b = {result.variable_values(b):g}")

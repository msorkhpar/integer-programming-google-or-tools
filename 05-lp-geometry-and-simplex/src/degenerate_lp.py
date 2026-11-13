"""Add "distribution at most twice transmission": three rows meet at the origin, and one pivot moves nowhere."""

from ortools.math_opt.python import mathopt

from simplex import solve
from split_lp import BOUNDS, ROWS, VALUE, build
from vertices import vertices

MIX = {**ROWS, "mix": ((1, -2), 0)}      # d <= 2t, written as d - 2t <= 0

for (d, t), tight in vertices({**MIX, **BOUNDS}).items():
    print(f"vertex ({d:g}, {t:g}): tight rows {', '.join(tight)}")

A = [list(a) for a, _ in MIX.values()]
b = [rhs for _, rhs in MIX.values()]
result = solve(A, b, VALUE, ["d", "t"] + [f"s_{label}" for label in MIX])
for entered, left, step, x, value in result.steps:
    print(f"{entered} enters, {left} leaves, step {step:g}: vertex ({x[0]:g}, {x[1]:g}), value {value:g}")
print(f"{result.status}: d = {result.x[0]:g}, t = {result.x[1]:g}, value {result.value:g}")
model, x = build(MIX)
glop = mathopt.solve(model, mathopt.SolverType.GLOP)
print(f"GLOP: {glop.termination.reason.name}, value {glop.objective_value():g}")

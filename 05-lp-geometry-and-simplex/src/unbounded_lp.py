"""Lose the budget and crew rows, and nothing stops d from growing: the LP is unbounded."""

from ortools.math_opt.python import mathopt

from simplex import solve
from split_lp import ROWS, VALUE, build

LOST = {"ready_t": ROWS["ready_t"]}      # the budget and crew rows failed to load

result = solve([[0, 1]], [20], VALUE, ["d", "t", "s_ready_t"])
print(f"tableau simplex: {result.status} at ({result.x[0]:g}, {result.x[1]:g}), direction {result.direction}")
model, x = build(LOST)
for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS):
    print(f"{solver.name}: {mathopt.solve(model, solver).termination.reason.name}")

check, _ = build(LOST, value=(0, 0))     # same rows, no objective: is there any plan at all?
print("same rows, zero objective, GLOP:", mathopt.solve(check, mathopt.SolverType.GLOP).termination.reason.name)

other = solve([[0, 1]], [20], (-1, 4), ["d", "t", "s_ready_t"])
print(f"same region, objective 4t - d: {other.status} at ({other.x[0]:g}, {other.x[1]:g}), value {other.value:g}")

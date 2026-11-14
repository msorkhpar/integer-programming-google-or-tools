"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from jobs import Limit, build

values = {"T1": 10, "T2": 6, "T3": 5, "T4": 4}
crane = Limit("crane_days", {"T1": 8, "T2": 7, "T3": 2, "T4": 3}, 12)
budget = Limit("budget", {"T1": 3, "T2": 3, "T3": 25, "T4": 4}, 20)


def lp_bound(limits):
    model, _ = build(values, limits, integer=False)
    return round(mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value(), 3)


def best_plan(limits):
    model, _ = build(values, limits)
    return round(mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value(), 3)


print("LP bound, crane only:", lp_bound([crane]))
print("best plan, crane only:", best_plan([crane]))
print("LP bound, crane and budget:", lp_bound([crane, budget]))
print("best plan, crane and budget:", best_plan([crane, budget]))

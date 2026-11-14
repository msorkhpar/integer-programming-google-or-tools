"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from street_trees import Street, build

# Three streets: tree breakpoints and shade benefit.
oak = Street("Oak", (0, 8, 20), (0, 24, 36))
pine = Street("Pine", (0, 15, 30), (0, 30, 45))
lime = Street("Lime", (0, 4, 12), (0, 20, 28))


def best(streets, stock, fixed=None):
    model, trees = build(streets, stock)
    for name, value in (fixed or {}).items():
        trees[name].lower_bound = trees[name].upper_bound = value
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    return round(result.objective_value(), 2)


print("three streets with 30 trees:", best([oak, pine, lime], 30))
print("Oak fixed at 14 trees:", best([oak], 50, {"Oak": 14}))
print("Pine fixed at 20 trees:", best([pine], 50, {"Pine": 20}))
print("Oak fixed at 25 trees:", best([oak], 50, {"Oak": 25}))

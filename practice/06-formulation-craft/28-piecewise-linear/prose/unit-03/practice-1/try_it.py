"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from expansion import build

widths = [6.0, 2.0, 3.0]   # ML/day added by each of three stages


def allowed(plan):
    model, built = build(widths)
    for var, value in zip(built, plan):
        var.lower_bound = var.upper_bound = value
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("plan 6, 1, 0:", allowed([6.0, 1.0, 0.0]))
print("plan 5, 1, 0:", allowed([5.0, 1.0, 0.0]))
print("plan 6, 2, 2.5:", allowed([6.0, 2.0, 2.5]))
print("plan 6, 0, 1:", allowed([6.0, 0.0, 1.0]))
print("plan 3, 0, 0:", allowed([3.0, 0.0, 0.0]))

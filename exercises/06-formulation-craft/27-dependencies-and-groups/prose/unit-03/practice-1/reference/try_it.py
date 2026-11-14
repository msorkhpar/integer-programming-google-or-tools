"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from fleet import Bus, build

buses = [Bus("V1", 3), Bus("V2", 12), Bus("V3", 12), Bus("V4", 19)]

def solve_ok(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan):
    model, y = build(buses, 1, 12)
    for (bid, option), var in y.items():
        value = 1.0 if plan.get(bid) == option else 0.0
        if value > var.upper_bound:
            return False
        var.lower_bound = var.upper_bound = value
    return solve_ok(model)


base = {"V1": "keep", "V2": "keep", "V3": "electric", "V4": "diesel"}
print("V1 keep, V2 keep, V3 electric, V4 diesel:", allowed(base))
print("same with V4 keep:", allowed({**base, "V4": "keep"}))
print("same with V1 electric:", allowed({**base, "V1": "electric"}))
print("same with V2 missing:", allowed({b: o for b, o in base.items() if b != "V2"}))

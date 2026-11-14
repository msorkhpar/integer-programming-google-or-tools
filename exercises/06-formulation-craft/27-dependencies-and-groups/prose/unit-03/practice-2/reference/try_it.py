"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from roofs import build

# Two dormitory roofs, 2027 to 2034.
years = tuple(range(2027, 2035))
roofs = {"DORM-A": (years, years), "DORM-B": ((2027, 2028), (2031, 2032, 2033))}

def accepted(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(patches, replacements, gap=2, warranty=3):
    model, patch, replace = build(roofs, gap, warranty)
    for chosen, variables in ((patches, patch), (replacements, replace)):
        for key, var in variables.items():
            var.lower_bound = var.upper_bound = 1.0 if key in chosen else 0.0
    return accepted(model)


print("DORM-A patch 2028, replace 2030:", allowed({("DORM-A", 2028)}, {("DORM-A", 2030)}))
print("DORM-A patch 2028, replace 2029:", allowed({("DORM-A", 2028)}, {("DORM-A", 2029)}))
print("DORM-A replace 2029, patch 2032:", allowed({("DORM-A", 2032)}, {("DORM-A", 2029)}))
print("DORM-A replace 2029, patch 2033:", allowed({("DORM-A", 2033)}, {("DORM-A", 2029)}))
print("DORM-B patch 2027, replace 2031:", allowed({("DORM-B", 2027)}, {("DORM-B", 2031)}))

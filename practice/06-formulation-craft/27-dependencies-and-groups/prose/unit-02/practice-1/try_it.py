"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from rail import Project, build

works = [
    Project("SIG-X1", (2031, 2032)),
    Project("SIG-X2", (2032, 2033)),
    Project("STN-E", (2032, 2033)),
    Project("TRK-9", (2031, 2032, 2033)),
]
blocks = [["SIG-X1", "SIG-X2"]]
platforms = {"STN-E": ["TRK-9"]}

def solve_ok(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan):
    model, x = build(works, blocks, platforms)
    for key, var in x.items():
        value = 1.0 if key in plan else 0.0
        if value > var.upper_bound:
            return False
        var.lower_bound = var.upper_bound = value
    return solve_ok(model)


print("SIG-X1 and SIG-X2 in 2032:", allowed({("SIG-X1", 2032), ("SIG-X2", 2032)}))
print("SIG-X1 in 2031 alone:", allowed({("SIG-X1", 2031)}))
print("SIG-X1 2031, SIG-X2 2032:", allowed({("SIG-X1", 2031), ("SIG-X2", 2032)}))
print("TRK-9 2031, STN-E 2032:", allowed({("TRK-9", 2031), ("STN-E", 2032)}))
print("TRK-9 2032, STN-E 2032:", allowed({("TRK-9", 2032), ("STN-E", 2032)}))

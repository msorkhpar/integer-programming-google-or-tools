"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from schools import Project, build

works = [
    Project("ROOF-E", (2031, 2032, 2033)),
    Project("RAMP-E", (2031, 2032, 2033)),
    Project("LIFT-E", (2032, 2033)),
    Project("PAINT-W", (2031, 2032)),
]
required = {"ROOF-E": 2032}
access = {"East": ["RAMP-E", "LIFT-E"]}
targets = {"East": (1, 2032)}

def solve_ok(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan):
    model, x = build(works, required, access, targets)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    return solve_ok(model)


print("ROOF-E 2031, RAMP-E 2032:", allowed({("ROOF-E", 2031), ("RAMP-E", 2032)}))
print("ROOF-E 2033, RAMP-E 2032:", allowed({("ROOF-E", 2033), ("RAMP-E", 2032)}))
print("ROOF-E 2032, LIFT-E 2033:", allowed({("ROOF-E", 2032), ("LIFT-E", 2033)}))
print("RAMP-E 2031 only:", allowed({("RAMP-E", 2031)}))
print("ROOF-E 2031+2032, LIFT-E 2032:", allowed({("ROOF-E", 2031), ("ROOF-E", 2032), ("LIFT-E", 2032)}))

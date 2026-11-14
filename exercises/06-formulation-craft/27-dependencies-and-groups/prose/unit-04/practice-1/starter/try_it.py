"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from streets import Project, build

# Two mains and three streets above or beside them, 2027 to 2033.
years = tuple(range(2027, 2034))
projects = [Project("MAIN-PINE", (2027, 2028), 1), Project("MAIN-BAY", (2027, 2028, 2029), 2),
            Project("PAVE-PINE", years), Project("PAVE-BAY", years), Project("PAVE-HILL", years)]
after = {"PAVE-PINE": ("MAIN-PINE", 2), "PAVE-BAY": ("MAIN-BAY", 0)}

def accepted(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan):
    model, x = build(projects, after)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    return accepted(model)


print("MAIN-PINE 2027, PAVE-PINE 2030:", allowed({("MAIN-PINE", 2027), ("PAVE-PINE", 2030)}))
print("MAIN-PINE 2027, PAVE-PINE 2029:", allowed({("MAIN-PINE", 2027), ("PAVE-PINE", 2029)}))
print("PAVE-PINE 2031 alone:", allowed({("PAVE-PINE", 2031)}))
print("MAIN-BAY 2029, PAVE-BAY 2031:", allowed({("MAIN-BAY", 2029), ("PAVE-BAY", 2031)}))
print("MAIN-BAY 2029, PAVE-BAY 2030:", allowed({("MAIN-BAY", 2029), ("PAVE-BAY", 2030)}))
print("PAVE-HILL 2027 alone:", allowed({("PAVE-HILL", 2027)}))

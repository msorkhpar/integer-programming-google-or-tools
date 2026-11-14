"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from testing import Project, build

# Two substations and their relay testing, 2027 to 2030.
years = (2027, 2028, 2029, 2030)
projects = [Project("SUB-E", (2027, 2028, 2029)), Project("TEST-E", years),
            Project("SUB-W", (2028, 2029)), Project("TEST-W", (2029, 2030))]
testing = {"TEST-E": ("SUB-E", 1), "TEST-W": ("SUB-W", 3)}

def accepted(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan):
    model, x = build(projects, years, testing)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    return accepted(model)


print("SUB-E 2028, TEST-E 2029:", allowed({("SUB-E", 2028), ("TEST-E", 2029)}))
print("SUB-E 2028, TEST-E 2030:", allowed({("SUB-E", 2028), ("TEST-E", 2030)}))
print("SUB-E 2028 alone:", allowed({("SUB-E", 2028)}))
print("SUB-E 2029, TEST-E 2028:", allowed({("SUB-E", 2029), ("TEST-E", 2028)}))
print("SUB-W 2028 alone:", allowed({("SUB-W", 2028)}))
print("nothing built:", allowed(set()))

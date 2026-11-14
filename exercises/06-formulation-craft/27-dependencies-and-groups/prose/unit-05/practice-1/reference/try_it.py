"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from counties import Project, build

# Fiber projects in two counties, 2027 to 2029, in $k.
years = (2027, 2028, 2029)
projects = [Project("E1", "Elm", (300, 100), (2027, 2028)), Project("E2", "Elm", (200,), (2027, 2028, 2029)),
            Project("E3", "Elm", (350,), (2028, 2029)), Project("O1", "Oak", (400,), (2027, 2028, 2029)),
            Project("O2", "Oak", (100, 100), (2027, 2028))]
floor = {"Elm": 500, "Oak": 200}
cap = {"Elm": 800}
yearly_cap = {("Elm", 2028): 400}

def accepted(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan):
    model, x = build(projects, years, floor, cap, yearly_cap)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    return accepted(model)


print("E1 2027, E2 2029, O1 2027:", allowed({("E1", 2027), ("E2", 2029), ("O1", 2027)}))
print("E1 2027, O1 2027:", allowed({("E1", 2027), ("O1", 2027)}))
print("E1 2027, E2 2027, E3 2029, O2 2027:", allowed({("E1", 2027), ("E2", 2027), ("E3", 2029), ("O2", 2027)}))
print("E1 2027, E3 2028, O1 2029:", allowed({("E1", 2027), ("E3", 2028), ("O1", 2029)}))

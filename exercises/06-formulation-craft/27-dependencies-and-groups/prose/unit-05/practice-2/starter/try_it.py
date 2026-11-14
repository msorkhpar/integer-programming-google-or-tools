"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from board import Project, build

# A water board's candidates, cost in $k.
projects = [Project("R1", "maintenance", 180), Project("R2", "maintenance", 220),
            Project("R3", "maintenance", 90), Project("N1", "growth", 350),
            Project("N2", "growth", 200), Project("N3", "growth", 60)]

def accepted(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan, budget=900, use=0.7, low=0.35, high=0.6):
    model, x = build(projects, budget, use, low, high)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    return accepted(model)


print("R1 R2 N1 at budget 900:", allowed({"R1", "R2", "N1"}))
print("R1 N1 at budget 900:", allowed({"R1", "N1"}))
print("R1 R2 R3 N1 N3 at budget 900:", allowed({"R1", "R2", "R3", "N1", "N3"}))
print("R1 R2 R3 N2 at budget 900:", allowed({"R1", "R2", "R3", "N2"}))
print("R3 N1 N2 N3 at budget 900:", allowed({"R3", "N1", "N2", "N3"}))

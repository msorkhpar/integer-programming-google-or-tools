"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from feeders import Project, add_parent_rows, selection_variables

def solve_ok(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan):
    model = mathopt.Model()
    x = selection_variables(model, [Project(pid, 5, 1) for pid in ["HUB", "L1", "L2", "L3"]])
    add_parent_rows(model, x, "HUB", ["L1", "L2", "L3"])
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    return solve_ok(model)


print("plan HUB:", allowed({"HUB"}))
print("plan HUB L1 L3:", allowed({"HUB", "L1", "L3"}))
print("plan L2:", allowed({"L2"}))
print("plan L1 L2:", allowed({"L1", "L2"}))

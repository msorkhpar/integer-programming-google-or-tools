"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from order import Project, build

# Substation projects: id, transformers needed, cost ($k). Order 8 to 20 units, fee 15.
projects = [Project("K1", 5, 40), Project("K2", 4, 35), Project("K3", 3, 20),
            Project("K4", 9, 70), Project("K5", 0, 10)]


def solved(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def fix(variables, plan):
    for key, var in variables.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0


def allowed(plan, budget=5_000):
    model, x = build(projects, 8, 20, 15, budget)
    fix(x, plan)
    return solved(model)


print("K1+K2:", allowed({"K1", "K2"}))
print("K1 alone:", allowed({"K1"}))
print("K1+K2+K3+K4:", allowed({"K1", "K2", "K3", "K4"}))
print("K1+K3 at budget 70:", allowed({"K1", "K3"}, 70))
print("K1+K3 at budget 80:", allowed({"K1", "K3"}, 80))
print("K5 at budget 10:", allowed({"K5"}, 10))

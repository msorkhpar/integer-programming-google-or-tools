"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from towers import Upgrade, build

# Broadband upgrades: id, cost ($k). One ferry permit, one radio-plus-mast bundle.
upgrades = [Upgrade("R1", 90), Upgrade("M1", 50), Upgrade("F1", 45), Upgrade("F2", 30), Upgrade("Q1", 20)]
permits = {"ferry": (15, ["F1", "F2"])}
bundles = [("R1", "M1", 30)]


def solved(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def fix(variables, plan):
    for key, var in variables.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0


def allowed(plan, budget):
    model, x = build(upgrades, permits, bundles, budget)
    fix(x, plan)
    return solved(model)


print("F1 at budget 60:", allowed({"F1"}, 60))
print("F1 at budget 55:", allowed({"F1"}, 55))
print("F1+F2 at budget 90:", allowed({"F1", "F2"}, 90))
print("R1+M1 at budget 110:", allowed({"R1", "M1"}, 110))
print("R1+M1 at budget 105:", allowed({"R1", "M1"}, 105))
print("R1 alone at budget 95:", allowed({"R1"}, 95))
print("Q1 at budget 20:", allowed({"Q1"}, 20))

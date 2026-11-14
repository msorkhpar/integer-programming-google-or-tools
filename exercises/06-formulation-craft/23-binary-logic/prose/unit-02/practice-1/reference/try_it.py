"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from water_rules import Project, build

# Ten wastewater projects of cost 50 each, with four engineering rules.
projects = [Project(pid, 50) for pid in ("PL", "E1", "E2", "D", "V", "S", "SC", "OLD", "NEW", "LAB", "GIS")]
needs_any = {"PL": ["E1", "E2"]}
all_trigger = [(["D", "V"], "SC")]
never_with = [("OLD", "NEW")]
together = [("LAB", "GIS")]


def solved(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def fix(variables, plan):
    for key, var in variables.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0


def allowed(plan):
    model, x = build(projects, 5_000, needs_any, all_trigger, never_with, together)
    fix(x, plan)
    return solved(model)


print("PL + E2:", allowed({"PL", "E2"}))
print("PL alone:", allowed({"PL"}))
print("D + V:", allowed({"D", "V"}))
print("D + V + SC:", allowed({"D", "V", "SC"}))
print("OLD + NEW:", allowed({"OLD", "NEW"}))
print("GIS alone:", allowed({"GIS"}))

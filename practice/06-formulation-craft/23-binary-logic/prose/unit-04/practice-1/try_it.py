"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from streets import Street, build

# Street rebuilds: id, cost. One detour pair and one three-street corridor.
streets = [Street("A", 70), Street("B", 60), Street("C", 40), Street("D", 30), Street("E", 20), Street("Z", 15)]
detours = {("A", "B"): 20}
corridors = [(["C", "D", "E"], 10)]


def solved(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def fix(variables, plan):
    for key, var in variables.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0


def allowed(plan, budget):
    model, x = build(streets, detours, corridors, budget)
    fix(x, plan)
    return solved(model)


print("A+B at budget 150:", allowed({"A", "B"}, 150))
print("A+B at budget 140:", allowed({"A", "B"}, 140))
print("C+D+E at budget 95:", allowed({"C", "D", "E"}, 95))
print("C+D+E at budget 100:", allowed({"C", "D", "E"}, 100))
print("C+D at budget 70:", allowed({"C", "D"}, 70))

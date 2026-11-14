"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from inspection import Pipe, build

# Five sewer mains: id, length (km), inspection cost ($k).
mains = [Pipe("M1", 18.0, 90), Pipe("M2", 10.0, 70), Pipe("M3", 22.0, 50),
         Pipe("M4", 9.0, 35), Pipe("M5", 4.0, 25)]


def allowed(plan, budget):
    model, x = build(mains, 25.0, 40, 2, budget)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("M1+M2 at budget 250:", allowed({"M1", "M2"}, 250))
print("M1+M2 at budget 220:", allowed({"M1", "M2"}, 220))
print("M1+M3+M5 at budget 1000:", allowed({"M1", "M3", "M5"}, 1000))
print("M4 alone at budget 70:", allowed({"M4"}, 70))
print("no mains at budget 0:", allowed(set(), 0))

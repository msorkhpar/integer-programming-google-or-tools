"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from relining import Pipe, build

# Mains to reline: id, length, minimum liner thickness (mm). Resin supply 80.
pipes = [Pipe("L1", 9.0, 5.0), Pipe("L2", 5.0, 7.0), Pipe("L3", 10.0, 3.5)]


def allowed(plan, thickness):
    model, x, t = build(pipes, 3.0, 9.0, 80.0)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    t.lower_bound = t.upper_bound = thickness
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("L2 at 7 mm:", allowed({"L2"}, 7.0))
print("L2 at 6 mm:", allowed({"L2"}, 6.0))
print("L1+L3 at 4 mm:", allowed({"L1", "L3"}, 4.0))
print("L1+L3 at 5 mm:", allowed({"L1", "L3"}, 5.0))
print("L3 at 4 mm:", allowed({"L3"}, 4.0))

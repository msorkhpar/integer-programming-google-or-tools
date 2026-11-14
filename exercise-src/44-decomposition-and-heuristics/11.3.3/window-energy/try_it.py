"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import datetime

from ortools.math_opt.python import mathopt

from energy import add_energy_rows

# (crane days, first day allowed, day it must end by), in a 15-day month
lifts = {"valve": (3, 0, 5), "pump": (4, 1, 6), "tank": (6, 0, 15), "mast": (3, 9, 14)}


def allowed(month):
    model = mathopt.Model()
    x = {n: model.add_binary_variable(name=n) for n in lifts}
    rows = add_energy_rows(model, x, lifts)
    for n, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if n in month else 0.0
    params = mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return len(rows), result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("rows, allowed for valve+mast:", allowed({"valve", "mast"}))
print("rows, allowed for valve+pump:", allowed({"valve", "pump"}))
print("rows, allowed for valve+tank+mast:", allowed({"valve", "tank", "mast"}))

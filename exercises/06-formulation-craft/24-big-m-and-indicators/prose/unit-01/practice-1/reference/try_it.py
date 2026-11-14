"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from floor import add_floor, spend_variables

# Two spend lines with (lowest, highest) amounts; the district floor is 70.
orders = {"paving": (10, 50), "signs": (5, 40)}


def allowed(values, waiver, floor=70):
    model = mathopt.Model()
    spend = spend_variables(model, orders)
    w = model.add_binary_variable(name="waiver")
    add_floor(model, spend, floor, w)
    for name, var in spend.items():
        var.lower_bound = var.upper_bound = values[name]
    w.lower_bound = w.upper_bound = waiver
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("paving 40, signs 35, no waiver:", allowed({"paving": 40, "signs": 35}, 0))
print("paving 30, signs 20, no waiver:", allowed({"paving": 30, "signs": 20}, 0))
print("paving 10, signs 5, waiver:", allowed({"paving": 10, "signs": 5}, 1))
print("paving 10, signs 5, no waiver:", allowed({"paving": 10, "signs": 5}, 0))

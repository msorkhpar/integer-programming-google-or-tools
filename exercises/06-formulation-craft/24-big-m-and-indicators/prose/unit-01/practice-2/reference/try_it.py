"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from dock import add_dock_row, choice_variables, dock_m

# Pallets per shipping option for three orders; the dock holds 10.
orders = {"R1": {"crate": 3, "pallet": 6}, "R2": {"crate": 2, "pallet": 5}, "R3": {"box": 1, "pallet": 4}}


def allowed(plan, overflow):
    model = mathopt.Model()
    choose = choice_variables(model, orders)
    yard = model.add_binary_variable(name="overflow")
    add_dock_row(model, choose, orders, 10, yard)
    for (o, opt), var in choose.items():
        var.lower_bound = var.upper_bound = 1.0 if plan.get(o) == opt else 0.0
    yard.lower_bound = yard.upper_bound = overflow
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("M at capacity 10:", dock_m(orders, 10))
print("M at capacity 20:", dock_m(orders, 20))
print("crate, crate, pallet, no yard:", allowed({"R1": "crate", "R2": "crate", "R3": "pallet"}, 0))
print("all pallets, no yard:", allowed({"R1": "pallet", "R2": "pallet", "R3": "pallet"}, 0))
print("all pallets, yard:", allowed({"R1": "pallet", "R2": "pallet", "R3": "pallet"}, 1))

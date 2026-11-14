"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from shortlist import shortlist


def barges(trips_integer: bool, tonnes_integer: bool) -> mathopt.Model:
    model = mathopt.Model(name="barges")
    trips = model.add_variable(lb=0, ub=5, is_integer=trips_integer, name="trips")
    tonnes = model.add_variable(lb=0, ub=200, is_integer=tonnes_integer, name="tonnes")
    model.add_linear_constraint(tonnes <= 45 * trips, name="load")
    model.maximize(3 * tonnes - 50 * trips)
    return model


print("all continuous:", [s.name for s in shortlist(barges(False, False))])
print("integer trips, continuous tonnes:", [s.name for s in shortlist(barges(True, False))])
print("all integer:", [s.name for s in shortlist(barges(True, True))])
print("all continuous, duals wanted:", [s.name for s in shortlist(barges(False, False), need_duals=True)])
print("integer trips, duals wanted:", [s.name for s in shortlist(barges(True, False), need_duals=True)])

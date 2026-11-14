"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from upgrade import add_bigm_modes, add_hull_modes, mode_variables


def allowed(spend, gain, rebuild):
    model = mathopt.Model()
    s, g, r = mode_variables(model)
    add_hull_modes(model, s, g, r)
    for var, value in ((s, spend), (g, gain), (r, rebuild)):
        var.lower_bound = var.upper_bound = value
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def lp_bound(rows):
    model = mathopt.Model()
    s, g, r = mode_variables(model, integer=False)
    rows(model, s, g, r)
    model.maximize(3 * g - s)
    return round(mathopt.solve(model, mathopt.SolverType.GLOP).objective_value(), 3)


print("line crew, spend 16, gain 8:", allowed(16, 8, 0))
print("line crew, spend 16, gain 9:", allowed(16, 9, 0))
print("rebuild, spend 90, gain 35:", allowed(90, 35, 1))
print("rebuild, spend 45, gain 10:", allowed(45, 10, 1))
print("LP bound, hull rows:", lp_bound(add_hull_modes))
print("LP bound, big-M rows:", lp_bound(add_bigm_modes))

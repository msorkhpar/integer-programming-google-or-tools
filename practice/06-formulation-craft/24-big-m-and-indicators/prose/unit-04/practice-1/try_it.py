"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from upgrade import add_bigm_modes, mode_variables


def allowed(spend, gain, rebuild):
    model = mathopt.Model()
    s, g, r = mode_variables(model)
    add_bigm_modes(model, s, g, r)
    for var, value in ((s, spend), (g, gain), (r, rebuild)):
        var.lower_bound = var.upper_bound = value
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


print("line crew, spend 24, gain 12:", allowed(24, 12, 0))
print("line crew, spend 24, gain 13:", allowed(24, 13, 0))
print("line crew, spend 35, gain 10:", allowed(35, 10, 0))
print("rebuild, spend 70, gain 38:", allowed(70, 38, 1))
print("rebuild, spend 55, gain 30:", allowed(55, 30, 1))

model = mathopt.Model()
s, g, r = mode_variables(model, integer=False)
add_bigm_modes(model, s, g, r)
model.maximize(3 * g - s)
print("LP bound of 3g - s:", round(mathopt.solve(model, mathopt.SolverType.GLOP).objective_value(), 3))

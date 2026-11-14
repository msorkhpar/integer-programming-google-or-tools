"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from cap import add_risk_caps

base = {2030: 400, 2031: 450}
cut = {("Line", 2030): {2030: 0, 2031: 90}, ("Trim", 2030): {2030: 30, 2031: 35}}


def allowed(plan: set, cap: dict) -> bool:
    model = mathopt.Model()
    x = {key: model.add_binary_variable(name=f"x_{key[0]}") for key in cut}
    add_risk_caps(model, x, base, cut, cap)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


cap = {2030: 380, 2031: 360}
print("no work, caps 380/360:", allowed(set(), cap))
print("Trim only, caps 380/360:", allowed({("Trim", 2030)}, cap))
print("Line only, caps 380/360:", allowed({("Line", 2030)}, cap))
print("Line and Trim, caps 380/360:", allowed(set(cut), cap))

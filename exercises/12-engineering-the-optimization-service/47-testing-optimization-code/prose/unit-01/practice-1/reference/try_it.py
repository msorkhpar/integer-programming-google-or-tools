"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from verdict import verdicts

# A school's projects: start years allowed and cost in the start year ($k); 60 per year.
windows = {"roof": (2031, 2032), "gym": (2031,), "boiler": (2032,)}
cost = {"roof": 45, "gym": 30, "boiler": 25}
model = mathopt.Model()
x = {(n, t): model.add_binary_variable(name=f"x_{n}_{t}") for n, years in windows.items() for t in years}
for n, years in windows.items():
    model.add_linear_constraint(sum(x[n, t] for t in years) <= 1, name=f"once_{n}")
for t in (2031, 2032):
    model.add_linear_constraint(sum(cost[n] * x[n, t] for n in windows if t in windows[n]) <= 60, name=f"budget_{t}")
x["roof", 2032].lower_bound = 1.0

plans = [{"roof": 2032, "gym": 2031}, {"roof": 2031, "gym": 2031}, {"roof": 2032, "boiler": 2032},
         {"roof": 2032, "gym": 2033}]
for plan, ok in zip(plans, verdicts(model, x, plans)):
    print(f"plan {plan}:", ok)
print("roof 2032 bounds afterwards:", (x["roof", 2032].lower_bound, x["roof", 2032].upper_bound))

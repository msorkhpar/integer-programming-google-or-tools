"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import datetime

from ortools.math_opt.python import mathopt

from renewals import Renewal, build

# A town's sewer relinings, $k.
relinings = [
    Renewal("S1", (2031, 2032), (60, 20), value=30),
    Renewal("S2", (2031, 2032), (45,), value=18),
    Renewal("S3", (2032, 2033), (25,), value=12, parent="S1", lag=1),
    Renewal("S4", (2032, 2033), (35,), value=15, group="Main-9"),
    Renewal("S5", (2032, 2033), (30,), value=14, group="Main-9"),
]
budgets = {2031: 80, 2032: 80, 2033: 80}


def allowed(plan):
    model, x = build(relinings, budgets)
    for (rid, t), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if plan.get(rid) == t else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


print("S1 2031, S3 2032, S4 2033:", allowed({"S1": 2031, "S3": 2032, "S4": 2033}))
print("S1 2031, S2 2031:", allowed({"S1": 2031, "S2": 2031}))
print("S1 2032, S3 2032:", allowed({"S1": 2032, "S3": 2032}))
print("S4 2032, S5 2033:", allowed({"S4": 2032, "S5": 2033}))
model, x = build(relinings, budgets)
result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=10)))
print("best value:", round(result.objective_value()), "starts:", sorted(k for k, v in x.items() if result.variable_values(v) > 0.5))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from rolling import add_rolling_caps

years = [2031, 2032, 2033, 2034, 2035]
# Spend by year, $k: a quay wall, a silo and a gate.
work = {"quay": {2031: 60, 2032: 60}, "silo": {2033: 90}, "gate": {2035: 50}}

def solve_ok(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan, k, cap):
    model = mathopt.Model()
    x = {name: model.add_binary_variable(name=name) for name in work}
    spend = {y: sum(cost.get(y, 0) * x[n] for n, cost in work.items()) for y in years}
    rows = add_rolling_caps(model, spend, years, k, cap)
    for name, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if name in plan else 0.0
    return sorted(rows), solve_ok(model)


print("quay+silo, k 2, cap 150:", allowed({"quay", "silo"}, 2, 150))
print("quay+silo, k 3, cap 150:", allowed({"quay", "silo"}, 3, 150))
print("silo+gate, k 3, cap 140:", allowed({"silo", "gate"}, 3, 140))
print("quay, k 6, cap 10:", allowed({"quay"}, 6, 10))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from advance import add_advances

# Spend by year, $k: a reservoir, a filter bed and a pipe bridge.
work = {"reservoir": {2031: 220}, "filters": {2031: 50, 2032: 100}, "bridge": {2033: 90}}

def solve_ok(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan, budgets, share):
    model = mathopt.Model()
    x = {name: model.add_binary_variable(name=name) for name in work}
    spend = {y: sum(cost.get(y, 0) * x[n] for n, cost in work.items()) for y in budgets}
    add_advances(model, spend, budgets, share)
    for name, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if name in plan else 0.0
    return solve_ok(model)


all_three = {"reservoir", "filters", "bridge"}
print("all three, budgets 250/200/90, share 0.2:", allowed(all_three, {2031: 250, 2032: 200, 2033: 90}, 0.2))
print("all three, budgets 250/200/90, share 0.1:", allowed(all_three, {2031: 250, 2032: 200, 2033: 90}, 0.1))
print("bridge, budgets 100/100/80, share 0.5:", allowed({"bridge"}, {2031: 100, 2032: 100, 2033: 80}, 0.5))
print("reservoir, budgets 200/150/0, share 0.2:", allowed({"reservoir"}, {2031: 200, 2032: 150, 2033: 0}, 0.2))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from booster import build

# A fan's curve: flow and power, slopes 2.0, 0.5, 1.5.
xs, ys = (0, 10, 30, 50), (0, 20, 30, 60)

def accepted(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(flow, power):
    model, q, p = build(xs, ys)
    q.lower_bound = q.upper_bound = flow
    p.lower_bound = p.upper_bound = power
    return accepted(model)


print("flow 20, power 25:", allowed(20, 25))
print("flow 40, power 45:", allowed(40, 45))
print("flow 20, power 24:", allowed(20, 24))
print("flow 20, power 30:", allowed(20, 30))
print("flow 50, power 60:", allowed(50, 60))
print("flow 55, power 70:", allowed(55, 70))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from fuel_order import build

# Heating oil: litres and total bill, 1.20 then 0.90 then 0.70 $ per litre.
xs, ys = (0, 10_000, 40_000, 60_000), (0, 12_000, 39_000, 53_000)

def accepted(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(volume, bill, audit, audit_above=20_000):
    model, v, b, a = build(xs, ys, audit_above)
    v.lower_bound = v.upper_bound = volume
    b.lower_bound = b.upper_bound = bill
    a.lower_bound = a.upper_bound = audit
    return accepted(model)


print("5000 L, bill 6000, no audit:", allowed(5_000, 6_000, 0))
print("5000 L, bill 5000, no audit:", allowed(5_000, 5_000, 0))
print("30000 L, bill 30000, audit:", allowed(30_000, 30_000, 1))
print("30000 L, bill 30000, no audit:", allowed(30_000, 30_000, 0))
print("20000 L, bill 21000, no audit:", allowed(20_000, 21_000, 0))
print("50000 L, bill 46000, audit:", allowed(50_000, 46_000, 1))

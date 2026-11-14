"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from retrofits import Retrofit, build

# Streetlight blocks in four wards: id, ward, cost.
blocks = ([Retrofit(f"A{k}", "Alder", 20 + k) for k in range(1, 5)]
          + [Retrofit(f"B{k}", "Birch", 30 + k) for k in range(1, 4)]
          + [Retrofit(f"C{k}", "Cedar", 15 + k) for k in range(1, 4)])
yards = {"Alder": 3, "Birch": 2}   # Cedar is not listed


def allowed(plan, share):
    model, x = build(blocks, 5_000, yards, share)
    for rid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if rid in plan else 0.0
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("A1 A2 B1 C1 at share 0.5:", allowed({"A1", "A2", "B1", "C1"}, 0.5))
print("A1 A2 A3 A4 B1 B2 C1 C2 at share 0.5:", allowed({"A1", "A2", "A3", "A4", "B1", "B2", "C1", "C2"}, 0.5))
print("A1 A2 B1 at share 0.5:", allowed({"A1", "A2", "B1"}, 0.5))
print("C1 C2 C3 A1 B1 at share 0.6:", allowed({"C1", "C2", "C3", "A1", "B1"}, 0.6))
print("C1 C2 C3 A1 B1 at share 0.4:", allowed({"C1", "C2", "C3", "A1", "B1"}, 0.4))

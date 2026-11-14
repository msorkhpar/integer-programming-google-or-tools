"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from loading import Order, Truck, build

orders = [Order("P1", 6, 700, 1.5), Order("P2", 3, 400, 2.0), Order("P3", 5, 650, 1.0, site="Quay"),
          Order("P4", 2, 300, 0.5, site="Quay"), Order("P5", 4, 500, 2.5)]
trucks = [Truck("V1", 1400, 3.0), Truck("V2", 1000, 4.0)]


def allowed(loads):
    model, x = build(orders, trucks)
    for (oid, tid), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if loads.get(oid) == tid else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


print("P1,P2 on V1:", allowed({"P1": "V1", "P2": "V1"}))
print("P1 on V1, P3,P4 on V2:", allowed({"P1": "V1", "P3": "V2", "P4": "V2"}))
print("P3 on V1, P4 on V2:", allowed({"P3": "V1", "P4": "V2"}))
print("P3 on V1 alone:", allowed({"P3": "V1"}))

model, x = build(orders, trucks)
result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print("best priority shipped:", round(result.objective_value(), 2))

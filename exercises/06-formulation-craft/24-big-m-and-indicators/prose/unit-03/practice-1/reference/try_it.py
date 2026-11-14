"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from pump import add_pump_rules, pump_variables


def allowed(flow_value, running, min_flow=35):
    model = mathopt.Model()
    flow, on = pump_variables(model)
    add_pump_rules(model, flow, on, min_flow)
    flow.lower_bound = flow.upper_bound = flow_value
    on.lower_bound = on.upper_bound = running
    result = mathopt.solve(model, mathopt.SolverType.GSCIP)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("idle, flow 0:", allowed(0, 0))
print("idle, flow 8:", allowed(8, 0))
print("running, flow 35:", allowed(35, 1))
print("running, flow 30:", allowed(30, 1))
print("running, flow 250000:", allowed(250_000, 1))

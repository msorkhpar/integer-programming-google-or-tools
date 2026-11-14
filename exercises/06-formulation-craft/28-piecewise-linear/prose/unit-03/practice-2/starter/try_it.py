"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from setpoints import build

# Five chiller setpoints: temperature (°C) and compressor power (kW).
temps = [5, 7, 9, 11, 13]
powers = [250, 210, 190, 200, 230]


def allowed(temp, power):
    model, t, p = build(temps, powers)
    t.lower_bound = t.upper_bound = temp
    p.lower_bound = p.upper_bound = power
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


model, _, _ = build(temps, powers)
print("binaries for 5 setpoints:", sum(v.integer for v in model.variables()))
print("9 °C at 190 kW:", allowed(9, 190))
print("9 °C at 250 kW:", allowed(9, 250))
print("10 °C at 195 kW:", allowed(10, 195))
print("13 °C at 230 kW:", allowed(13, 230))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from footer import read_footer

optimal = [
    "LP tanks has 4 rows; 5 cols; 12 nonzeros",
    "Presolving model",
    "Using EKK dual simplex solver - serial",
    "Model name          : tanks",
    "Model status        : Optimal",
    "Simplex   iterations: 5",
    "Objective value     :  2.7500000000e+02",
    "HiGHS run time      :          0.00",
]
stopped = optimal[:3] + [
    "Model name          : tanks",
    "Model status        : Time limit reached",
    "Simplex   iterations: 900",
    "Objective value     :  1.9000000000e+02",
]
print("optimal log:", read_footer(optimal))
print("time-limit log:", read_footer(stopped))

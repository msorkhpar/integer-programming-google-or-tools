"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from schedule import Crew, Job, build

years = [2030, 2031]
crews = [Crew("Ortiz", {2030: 18, 2031: 12}, 8, certified=True), Crew("Patel", {2030: 14, 2031: 14}, 6)]
jobs = [Job("W1", 2030, 2031, {"Ortiz": 9, "Patel": 11}),
        Job("W2", 2030, 2030, {"Ortiz": 7, "Patel": 7}),
        Job("W3", 2031, 2031, {"Ortiz": 10, "Patel": 12}, large=True)]

model, x = build(jobs, crews, years)
print("variables:", sorted(x))
result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print("status:", result.termination.reason.name)
print("cost:", round(result.objective_value(), 2))
values = result.variable_values()
print("schedule:", sorted(k for k, v in x.items() if values[v] > 0.5))

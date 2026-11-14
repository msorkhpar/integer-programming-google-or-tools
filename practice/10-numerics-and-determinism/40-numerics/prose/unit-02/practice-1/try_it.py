"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from extremes import matrix_extremes

model = mathopt.Model()
pumps = model.add_variable(lb=0, ub=50, name="pumps")
valves = model.add_variable(lb=0, ub=50, name="valves")
model.add_linear_constraint(80_000 * pumps + 12_000 * valves <= 2_000_000, name="capital")
model.add_linear_constraint(pumps + 0.05 * valves >= 6, name="flow")
smallest, largest = matrix_extremes(model)
print("smallest entry:", smallest)
print("largest entry:", largest)

model.add_linear_constraint(-3e7 * valves >= -9e8, name="insurance")
print("largest entry with an insurance row:", matrix_extremes(model)[1])

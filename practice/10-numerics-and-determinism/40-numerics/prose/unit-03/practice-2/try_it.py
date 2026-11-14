"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from audit import audit

model = mathopt.Model()
east = model.add_binary_variable(name="open_east")
vans = model.add_variable(lb=0, ub=30, name="vans")
model.add_linear_constraint(vans <= 20 * east, name="capacity")
model.add_linear_constraint(lb=5.0, ub=18.0, expr=vans, name="demand")

print("east 1, vans 12:", audit(model, {east: 1.0, vans: 12.0}))
print("east 0.9999993, vans 12:", {k: round(v, 9) for k, v in audit(model, {east: 0.9999993, vans: 12.0}).items()})
print("east 1, vans 32:", audit(model, {east: 1.0, vans: 32.0}))

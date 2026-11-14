"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from rows import describe, describe_model

model = mathopt.Model(name="ferries")
boat = model.add_integer_variable(lb=0, ub=10, name="boat")
coach = model.add_integer_variable(lb=0, ub=20, name="coach")
taxi = model.add_variable(lb=0, ub=40, name="taxi")

model.add_linear_constraint(1.5 * coach + 6 * boat <= 90, name="crew_hours")
model.add_linear_constraint(200 * boat + 50 * coach >= 1000, name="seats")
model.add_linear_constraint(taxi == 3 * coach, name="feeder")
ranged = model.add_linear_constraint((5 <= boat - coach + 0.25 * taxi) <= 12, name="mix")

print("one row:", describe(ranged))
for line in describe_model(model):
    print("row:", line)

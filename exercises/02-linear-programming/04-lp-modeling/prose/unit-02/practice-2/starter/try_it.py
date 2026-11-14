"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from report import binding, room

# Two kilns whose output is fixed by their bounds, so the solve returns exactly (30, 15).
model = mathopt.Model(name="kilns")
a = model.add_variable(lb=30, ub=30, name="a")
b = model.add_variable(lb=15, ub=15, name="b")
model.add_linear_constraint(2 * a + b <= 90, name="gas")
model.add_linear_constraint(a + b >= 40, name="order")
model.add_linear_constraint(lb=5, ub=15, expr=a - b, name="spread")
model.add_linear_constraint(a <= 2 * b, name="mix")
model.maximize(a + b)
result = mathopt.solve(model, mathopt.SolverType.GLOP)

for name, r in room(model, result).items():
    print(f"room of {name}:", round(r, 6))
print("binding rows:", binding(model, result))

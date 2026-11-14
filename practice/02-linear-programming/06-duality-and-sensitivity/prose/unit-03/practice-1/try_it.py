"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from entry import entry_values

# A council's road money ($k): value per $k of each kind of work.
model = mathopt.Model(name="roads")
x = {name: model.add_variable(lb=0, name=name) for name in ("potholes", "resurface", "signs", "lines")}
model.add_linear_constraint(sum(x.values()) <= 80, name="budget")
model.add_linear_constraint(x["potholes"] <= 30, name="pothole_crews")
model.maximize(0.9 * x["potholes"] + 0.7 * x["resurface"] + 0.4 * x["signs"] + 0.1 * x["lines"])

for name, value in entry_values(model).items():
    print(f"entry value of {name}:", round(value, 4))

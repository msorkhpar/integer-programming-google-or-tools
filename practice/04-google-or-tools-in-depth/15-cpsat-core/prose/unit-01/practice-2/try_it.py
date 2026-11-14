"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from report import report


def boxes(capacity):
    model = cp_model.CpModel()
    x = {name: model.new_bool_var(name) for name in ("ice", "fish", "bread", "fruit")}
    model.add(3 * x["ice"] + 5 * x["fish"] + 2 * x["bread"] + 4 * x["fruit"] <= capacity)
    model.maximize(4 * x["ice"] + 7 * x["fish"] + 2 * x["bread"] + 5 * x["fruit"])
    return model, x


solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10
print("capacity 9:", report(*boxes(9), solver))

model, x = boxes(9)
model.add(x["ice"] + x["fish"] >= 3)
print("capacity 9, three of two:", report(model, x))

model, x = boxes(9)
model.add(x["ice"] + x["fish"] <= 1).only_enforce_if(model.new_int_var(0, 3, "count"))
print("enforced by an integer:", report(model, x))

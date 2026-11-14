"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from rota import set_objectives

# A small ward: open early shifts, extra hours, and two liked shifts.
model = mathopt.Model(name="ward")
open_early = model.add_variable(lb=0, ub=6, name="open_early")
extra = model.add_variable(lb=0, ub=24, name="extra")
liked = [model.add_binary_variable(name=f"liked_{n}") for n in ("dee", "eli")]
set_objectives(model, 2 * open_early, 0.5 * extra + 1, liked[0] + 3 * liked[1])


def show(obj):
    terms = {t.variable.name: t.coefficient for t in obj.linear_terms()}
    return f"priority {obj.priority}, maximize {obj.is_maximize}, offset {obj.offset}, terms {terms}"


print("primary:", show(model.objective))
for obj in model.auxiliary_objectives():
    print(f"auxiliary {obj.name!r}:", show(obj))

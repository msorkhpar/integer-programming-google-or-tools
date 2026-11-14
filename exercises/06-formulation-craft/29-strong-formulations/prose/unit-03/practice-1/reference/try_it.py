"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from datetime import timedelta

from ortools.math_opt.python import mathopt

from fleet import build

days = {"Ash": 18, "Elm": 15, "Oak": 11, "Yew": 10, "Fir": 6}

for ordered in (False, True):
    fleet = build(days, 4, ordered=ordered)
    result = mathopt.solve(fleet.model, mathopt.SolverType.HIGHS,
                           params=mathopt.SolveParameters(time_limit=timedelta(seconds=5)))
    print(f"ordered={ordered} rows:", sum(1 for _ in fleet.model.linear_constraints()))
    print(f"ordered={ordered} units rented:", round(result.objective_value()),
          {s: k for (s, k), v in fleet.x.items() if result.variable_values(v) > 0.5})

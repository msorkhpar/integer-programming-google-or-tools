"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from hinting import build, hint_params

# name -> (profit, vans needed)
routes = {"quay": (35, 2), "spire": (24, 1), "canal": (19, 2), "abbey": (14, 1), "fort": (29, 3)}
model, y = build(routes, 5)
last_week = {"quay", "abbey"}

for complete in (True, False):
    params = hint_params(y, last_week, complete)
    for hint in params.solution_hints:
        print(f"hint, complete={complete}:", {v.name: val for v, val in sorted(hint.variable_values.items(), key=lambda kv: kv[0].name)})

log: list[str] = []
result = mathopt.solve(model, mathopt.SolverType.HIGHS, model_params=hint_params(y, last_week, True),
                       msg_cb=mathopt.list_message_callback(log))
print("HiGHS lines about the start:", [line for line in log if "MIP start" in line or "user-supplied" in line])
print("profit with the hint:", result.objective_value())

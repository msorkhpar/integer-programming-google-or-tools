"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from crosscheck import suspects

# (status, objective) reported by each solver on one model.
runs = {"Lark": ("OPTIMAL", 1450.0), "Wren": ("OPTIMAL", 1450.0), "Finch": ("OPTIMAL", 1452.0),
        "Robin": ("TIME_LIMIT", 1300.0)}
print("tolerance 1e-6:", suspects(runs, 1e-6))
print("tolerance 0.01:", suspects(runs, 0.01))
print("Robin OPTIMAL at 1300, tolerance 0.01:", suspects({**runs, "Robin": ("OPTIMAL", 1300.0)}, 0.01))
print("no OPTIMAL runs:", suspects({"Lark": ("INFEASIBLE", 0.0)}, 1e-6))

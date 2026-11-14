"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from port import set_objective_n_args

levels = [{"name": "coverage", "priority": 0, "maximize": True, "abs_tol": 1.5, "rel_tol": None},
          {"name": "travel", "priority": 1, "maximize": False, "abs_tol": None, "rel_tol": 0.03},
          {"name": "seniority", "priority": 2, "maximize": True, "abs_tol": None, "rel_tol": None}]

for args in set_objective_n_args(levels):
    print(f"{args['name']}:", args)

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from gurobipy import GRB

from iis_report import iis_report

# Rows and bounds as read from a model after computeIIS().
rows = [{"name": "dock_cover", "sense": ">", "rhs": 9.0, "iis": 1},
        {"name": "shift_cap", "sense": "<", "rhs": 7.0, "iis": 1},
        {"name": "one_lead", "sense": "=", "rhs": 1.0, "iis": 0}]
bounds = [{"name": "temps", "lb": 0.0, "ub": 2.0, "iis_lb": 0, "iis_ub": 1},
          {"name": "leads", "lb": 1.0, "ub": 3.0, "iis_lb": 0, "iis_ub": 0}]
print("INFEASIBLE:", iis_report(GRB.INFEASIBLE, rows, bounds))
print("INFEASIBLE, rows only:", iis_report(GRB.INFEASIBLE, rows, []))
print("OPTIMAL:", iis_report(GRB.OPTIMAL, rows, bounds))

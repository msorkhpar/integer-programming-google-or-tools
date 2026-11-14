"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

# Pyomo logs every set it builds and the whole solver log; keep its own logger to warnings.
logging.getLogger("pyomo").setLevel(logging.WARNING)

from overtime import plan

# Bus garage jobs: name -> (hours, value $); overtime curve through (hours, cost).
jobs = {"engine": (25, 2000), "gearbox": (15, 1100), "seats": (10, 500), "glass": (20, 700)}
hours = [0, 8, 16, 30]
cost = [0, 280, 720, 1700]
for regular in (50, 35):
    net, over, pay = plan(jobs, regular, hours, cost)
    print(f"regular {regular}h: net {round(net, 2)}, overtime {round(over, 2)}h costing {round(pay, 2)}")

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from solve import Project, solve_plan

# Four dock repairs; L1 is ordered by the port authority.
docks = [
    Project("L1", 40, 50, must_do=True),
    Project("L2", 35, 60),
    Project("L3", 25, 41),
    Project("L4", 20, 22),
]

print("budget 100:", solve_plan(docks, 100))
print("budget 65:", solve_plan(docks, 65))
print("budget 30:", solve_plan(docks, 30))

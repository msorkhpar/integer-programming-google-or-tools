"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from selection import Project, solve

# Six depot upgrades; D1 is ordered by the inspector.
depots = [
    Project("D1", 30, 45, must_do=True),
    Project("D2", 20, 30),
    Project("D3", 10, 35, parent="D2"),
    Project("D4", 25, 33, group="roof"),
    Project("D5", 15, 26, group="roof"),
    Project("D6", 35, 30),
]

for budget in (120, 80, 40):
    value, plan = solve(depots, budget)
    print(f"budget {budget}:", round(value), sorted(plan))

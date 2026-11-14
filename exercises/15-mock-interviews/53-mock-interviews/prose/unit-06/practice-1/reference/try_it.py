"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from checker import Limits, Project, broken_rules

piers = [
    Project("P1", 50, 2, "East"),
    Project("P2", 35, 3, "East"),
    Project("P3", 25, 2, "West"),
    Project("P4", 40, 4, "West"),
    Project("P5", 15, 1, "North"),
]
limits = Limits(budget=110, crew=8, region_cap={"East": 1, "West": 2, "North": 1},
                conflicts=[("P1", "P4")], needs=[("P5", "P3")])

for plan in ({"P1", "P3", "P5"}, {"P1", "P2"}, {"P1", "P4"}, {"P5"}, {"P1", "P2", "P3", "P4"}):
    print(f"plan {sorted(plan)}:", broken_rules(plan, piers, limits))

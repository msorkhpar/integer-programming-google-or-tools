"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rows import Project, broken_rows

# Five mains renewals at budget 90.
renewals = [
    Project("R1", 35, 50, must_do=True),
    Project("R2", 25, 30),
    Project("R3", 20, 28, parent="R2"),
    Project("R4", 15, 22, group="pump"),
    Project("R5", 10, 14, group="pump"),
]
for plan in ({"R1", "R2", "R3"}, {"R1", "R3", "R4", "R5"}, {"R2", "R3", "R4"}, {"R1", "R2", "R3", "R4"}):
    print(f"plan {sorted(plan)}:", sorted(broken_rows(plan, renewals, 90)))

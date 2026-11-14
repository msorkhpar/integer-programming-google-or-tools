"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from dual import dual_fixings

# Tree-trimming crews: "overtime" costs money, "permit" is a prerequisite with a -1 entry.
objective = {"trim_a": 6, "trim_b": 4, "overtime": -3, "permit": 1, "survey": 2}
rows = {
    "crew_hours": ({"trim_a": 3, "trim_b": 2, "overtime": 1}, 5),
    "needs_permit": ({"trim_b": 1, "permit": -1}, 0),
}

print("fixings as given:", dual_fixings(objective, rows))
print("fixings with overtime worth 0:", dual_fixings({**objective, "overtime": 0}, rows))

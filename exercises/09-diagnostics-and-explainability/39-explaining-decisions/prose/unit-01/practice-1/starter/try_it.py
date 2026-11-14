"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from slacks import Row, binding, slack

rows = [
    Row("yard_bays", {"tram_x": 10, "tram_y": 8}, "<=", 50),
    Row("low_floor_min", {"tram_y": 1, "tram_z": 1}, ">=", 3),
    Row("depot_lease", {"lease": 1}, "==", 1),
]
plan = {"tram_x": 2, "tram_y": 2, "tram_z": 1, "lease": 1}

for row in rows:
    print(f"slack of {row.name}:", slack(row, plan))
print("binding rows:", binding(rows, plan))
print("binding rows, lease 0:", binding(rows, {**plan, "lease": 0}))

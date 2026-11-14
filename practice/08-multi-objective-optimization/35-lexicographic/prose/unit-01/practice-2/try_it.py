"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from packages import accepted

bridges = {"pine":  {"safety": 70.0, "cost": 6.0, "jobs": 8.0},
           "cedar": {"safety": 70.0, "cost": 5.0, "jobs": 6.0},
           "fir":   {"safety": 67.0, "cost": 2.5, "jobs": 15.0},
           "larch": {"safety": 55.0, "cost": 3.0, "jobs": 25.0}}

print("safety exact, then cost:", accepted(bridges, [("safety", True, 0.0, 0.0), ("cost", False, 0.0, 0.0)]))
print("safety within 5%, then cost:", accepted(bridges, [("safety", True, 0.0, 0.05), ("cost", False, 0.0, 0.0)]))
print("safety within 20, then jobs:", accepted(bridges, [("safety", True, 20.0, 0.0), ("jobs", True, 0.0, 0.0)]))
print("safety only, exact:", accepted(bridges, [("safety", True, 0.0, 0.0)]))

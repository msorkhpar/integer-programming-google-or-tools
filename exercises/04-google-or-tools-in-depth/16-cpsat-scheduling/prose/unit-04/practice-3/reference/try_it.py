"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from handout import name_crews

# Each job is (start_day, days, crews needed).
jobs = {"roof": (4, 2, 2), "fence": (0, 3, 1), "patio": (1, 2, 1), "shed": (3, 1, 1)}
named = name_crews(jobs, ["P", "Q", "R"])
for name in sorted(named, key=lambda n: jobs[n][0]):
    print(f"{name} {jobs[name]} gets crews:", named[name])

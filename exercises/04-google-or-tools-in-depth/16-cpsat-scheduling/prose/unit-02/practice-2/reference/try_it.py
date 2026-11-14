"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from gang_days import holiday_plan

# Three gangs most days; only one on days 3 and 4 (a holiday).
jobs = {"birch": (2, 2), "maple": (3, 1), "pine": (2, 1)}
available = [3, 3, 3, 1, 1, 3, 3, 3, 3, 3]
start = holiday_plan(jobs, available)
for name in sorted(start):
    print(f"{name} (days, gangs = {jobs[name]}) starts on day:", start[name])
print("last job ends on day:", max(start[n] + d for n, (d, _) in jobs.items()))

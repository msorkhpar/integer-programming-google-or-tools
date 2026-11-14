"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from possessions import possession_plan

# Each job is (line, days); each line has its closures as (first_day, last_day).
jobs = {"ballast": ("up", 2), "signals": ("up", 4), "culvert": ("down", 3)}
possessions = {"up": [(0, 2), (6, 11)], "down": [(4, 8)]}
start = possession_plan(jobs, possessions)
for name in sorted(start):
    print(f"{name} {jobs[name]} starts on day:", start[name])
print("last job ends on day:", max(start[n] + d for n, (_, d) in jobs.items()))

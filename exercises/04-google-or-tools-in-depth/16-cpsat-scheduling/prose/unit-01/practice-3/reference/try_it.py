"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from teams import split_work

# Three sewer jobs, two crews; green is away on days 0 to 2.
jobs = {"canal_st": 4, "bridge": 2, "outfall": 3}
away = {"green": [(0, 2)]}

plan = split_work(jobs, ["amber", "green"], away, 15)
for job, (team, start) in sorted(plan.items()):
    print(f"{job}: team {team}, start day {start}")
print("last day of work ends at:", max(s + jobs[j] for j, (_, s) in plan.items()))
print("one team only:", split_work(jobs, ["amber"], {}, 15))

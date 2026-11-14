"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rig import shortest_schedule

# Four pipe welds share one rig; the rig is booked for days 3 to 4.
jobs = {"P1": 2, "P2": 3, "P3": 1, "P4": 2}
start = shortest_schedule(jobs, [(3, 4)], 25)
for name in sorted(start):
    print(f"{name} ({jobs[name]} days) starts on day:", start[name])
print("last weld ends on day:", max(start[n] + d for n, d in jobs.items()))

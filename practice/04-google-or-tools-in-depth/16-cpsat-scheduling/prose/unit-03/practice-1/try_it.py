"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from courier import cheapest_runs

# Each run lists (hours per vehicle, cost per vehicle): vehicle 0 is a van, 1 a motorbike.
runs = {"docks": ([3, 2], [18, 26]), "uptown": ([5, 2], [25, 40]), "depot": ([2, 1], [8, 11])}
for deadline in (12, 7, 5):
    total, plan = cheapest_runs(runs, deadline)
    print(f"deadline {deadline}h: cost {total}, (vehicle, start) {plan}")

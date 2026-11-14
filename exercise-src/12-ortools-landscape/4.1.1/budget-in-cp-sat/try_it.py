"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pick import pick

# Repairs: values (scores) and costs in $M with cents.
values = [6, 9, 4, 7]
costs = [0.45, 0.80, 0.30, 0.55]

print("pick at budget 1.30:", pick(values, costs, 1.30))
print("pick at budget 1.29:", pick(values, costs, 1.29))
print("pick at budget 2.10:", pick(values, costs, 2.10))

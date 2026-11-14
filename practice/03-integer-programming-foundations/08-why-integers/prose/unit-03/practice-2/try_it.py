"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from within import count_within

print("costs [25, 35, 50] within 60:", count_within([25, 35, 50], 60))
print("costs [25, 35, 50] within 110:", count_within([25, 35, 50], 110))
print("costs [5, 10, 15, 20] within 25:", count_within([5, 10, 15, 20], 25))
print("no costs within 10:", count_within([], 10))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rins import rins

# Four feeder upgrades.
values = {"F1": 8, "F2": 6, "F3": 4, "F4": 3}
costs = {"F1": 6, "F2": 4, "F3": 3, "F4": 2}
incumbent = {"F1": 1, "F2": 0, "F3": 0, "F4": 1}

print("plan at budget 9, LP agrees on F1, F4:", rins(values, costs, 9, incumbent, {"F1": 1, "F2": 0.5, "F3": 0.5, "F4": 1}))
print("plan at budget 9, LP agrees on F4 only:", rins(values, costs, 9, incumbent, {"F1": 0.3, "F2": 1, "F3": 1, "F4": 1}))
print("plan at budget 7, LP agrees on all:", rins(values, costs, 7, incumbent, {"F1": 1, "F2": 0, "F3": 0, "F4": 1}))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from search import best_plan

# Spare pumps: (name, value, cost); "R9" is required by the regulator.
pumps = [("P1", 90, 30), ("P2", 80, 40), ("P3", 36, 36), ("P4", 20, 40), ("R9", 8, 20)]

print("plan at budget 100, must R9:", best_plan(pumps, 100, {"R9"}))
print("plan at budget 100, must nothing:", best_plan(pumps, 100, set()))
print("plan at budget 15, must R9:", best_plan(pumps, 15, {"R9"}))

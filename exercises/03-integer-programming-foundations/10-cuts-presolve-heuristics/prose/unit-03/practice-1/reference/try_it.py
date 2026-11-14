"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fill import round_and_fill

# Four transformer replacements.
values = {"T1": 10, "T2": 6, "T3": 4, "T4": 1}
costs = {"T1": 5, "T2": 4, "T3": 2, "T4": 1}

print("plan at budget 9, T2 at 0.75:", round_and_fill(values, costs, 9, {"T1": 1, "T2": 0.75, "T3": 0, "T4": 0}))
print("plan at budget 12, T1 at 0.5:", round_and_fill(values, costs, 12, {"T1": 0.5, "T2": 1, "T3": 1, "T4": 1}))
print("plan at budget 6, all at 0:", round_and_fill(values, costs, 6, dict.fromkeys(values, 0)))

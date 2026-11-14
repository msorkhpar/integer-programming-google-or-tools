"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from downward import step_points

costs, values = [2, 5, 6], [4, 9, 11]

print("steps between budgets 0 and 13:", step_points(costs, values, 0, 13))
print("steps between budgets 9 and 13:", step_points(costs, values, 9, 13))

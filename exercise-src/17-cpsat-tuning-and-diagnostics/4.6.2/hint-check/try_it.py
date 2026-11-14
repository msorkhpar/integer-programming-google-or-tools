"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from carryover import fits

# Four batches of meter swaps; batch Q is required; 100 to spend.
costs = {"P": 35, "Q": 45, "R": 25, "S": 30}
values = {"P": 60, "Q": 40, "R": 50, "S": 55}
for plan in ({"Q", "R", "S"}, {"P", "Q", "R"}, {"P", "R", "S"}, {"P", "Q"}):
    print(f"plan {sorted(plan)} fits:", fits(costs, values, {"Q"}, 100, plan))

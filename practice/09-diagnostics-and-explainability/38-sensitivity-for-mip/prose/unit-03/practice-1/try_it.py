"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from sweep import sweep

costs, values = [3, 5, 2], [7, 9, 3]

for budget, best in sweep(costs, values, [], [1, 3, 5, 8, 10]):
    print(f"best value at budget {budget}, nothing required:", best)
print("upgrade 1 required, budgets 4 and 7:", sweep(costs, values, [1], [4, 7]))

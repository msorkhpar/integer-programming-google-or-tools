"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

# Pyomo logs every set it builds and the whole solver log; keep its own logger to warnings.
logging.getLogger("pyomo").setLevel(logging.WARNING)

from sweep import sweep

# Sewer relinings: name -> (cost $k, value $k).
sewers = {"S1": (35, 50), "S2": (25, 33), "S3": (20, 28), "S4": (10, 12)}
budgets = [10, 30, 55, 100, 45]
for budget, value in zip(budgets, sweep(sewers, budgets)):
    print(f"best value at budget {budget}:", round(value, 2))

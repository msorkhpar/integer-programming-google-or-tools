"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from price_function import is_dual_feasible

hours, silt = [3, 4], [4, 6]          # two dredging job types

print("F = 1.5 per hour:", is_dual_feasible([1.5 * d for d in range(9)], hours, silt))
print("F = 1.2 per hour:", is_dual_feasible([1.2 * d for d in range(9)], hours, silt))
print("F = [0, 0, 0, 4, 6, 6, 8, 10, 12]:", is_dual_feasible([0, 0, 0, 4, 6, 6, 8, 10, 12], hours, silt))
print("F = [0, -1, 0, 4, 6, 6, 8, 10, 12]:", is_dual_feasible([0, -1, 0, 4, 6, 6, 8, 10, 12], hours, silt))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from violation import total_violation

print("x + y <= 8, x >= 1, y >= 2:", round(total_violation([([1, 1], "<=", 8), ([1, 0], ">=", 1), ([0, 1], ">=", 2)]), 6))
print("x + y <= 8, x + y >= 13:", round(total_violation([([1, 1], "<=", 8), ([1, 1], ">=", 13)]), 6))
print("x >= 6, x <= 1, 3x <= 6:", round(total_violation([([1], ">=", 6), ([1], "<=", 1), ([3], "<=", 6)]), 6))

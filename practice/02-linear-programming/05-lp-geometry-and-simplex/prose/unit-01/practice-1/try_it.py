"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from vertices import vertices

# Each row (a, b, r) means a*x + b*y <= r.
x_nonneg, y_nonneg = (-1, 0, 0), (0, -1, 0)

print("x + 2y <= 6:", vertices([x_nonneg, y_nonneg, (1, 2, 6)]))
print("x <= 4, y <= 3, x + y <= 5:", vertices([x_nonneg, y_nonneg, (1, 0, 4), (0, 1, 3), (1, 1, 5)]))
print("x <= 2 only:", vertices([x_nonneg, y_nonneg, (1, 0, 2)]))

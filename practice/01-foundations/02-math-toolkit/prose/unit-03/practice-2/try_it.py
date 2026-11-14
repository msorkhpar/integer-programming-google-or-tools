"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import numpy as np

from corner import best_corner

# A farm splits land between wheat (x0) and barley (x1).
#   x0 + x1 <= 10, 2 x0 + x1 <= 14, x0 >= 0, x1 >= 0
A = np.array([[1, 1], [2, 1], [-1, 0], [0, -1]])
b = np.array([10, 14, 0, 0])

print("best corner for profit 3 x0 + 2 x1:", best_corner(A, b, np.array([3, 2])))
print("best corner for profit 1 x0 + 3 x1:", best_corner(A, b, np.array([1, 3])))
print("best corner for profit 5 x0 + 1 x1:", best_corner(A, b, np.array([5, 1])))

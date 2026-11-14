"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import numpy as np

from stopping import converged

# min 4 x1 + 5 x2  s.t.  2 x1 + x2 >= 6,  x1 + 2 x2 >= 6,  x >= 0; optimum x = (2, 2), prices (1, 2)
A = np.array([[2.0, 1.0], [1.0, 2.0]])
b = np.array([6.0, 6.0])
c = np.array([4.0, 5.0])
x, y = np.array([2.0, 2.0]), np.array([1.0, 2.0])

print("x (2, 2), y (1, 2), eps 1e-6:", converged(A, b, c, x, y, 1e-6))
print("x (2.2, 2.2), y (1, 2), eps 1e-6:", converged(A, b, c, 1.1 * x, y, 1e-6))
print("x (1.9, 2), y (1, 2), eps 1e-6:", converged(A, b, c, np.array([1.9, 2.0]), y, 1e-6))
print("x (1.9, 2), y (1, 2), eps 0.1:", converged(A, b, c, np.array([1.9, 2.0]), y, 0.1))
print("x (2, 2), y (3, 0), eps 1e-6:", converged(A, b, c, x, np.array([3.0, 0.0]), 1e-6))

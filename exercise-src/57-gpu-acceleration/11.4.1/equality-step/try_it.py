"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import numpy as np

from blend import pdhg_step, solve

# min 2 x1 + 1 x2 + 3 x3  s.t.  x1 + x2 + x3 = 6,  x1 - x2 = 1,  0 <= x <= 4
A = np.array([[1.0, 1.0, 1.0], [1.0, -1.0, 0.0]])
b = np.array([6.0, 1.0])
c = np.array([2.0, 1.0, 3.0])
u = np.array([4.0, 4.0, 4.0])

x, y = pdhg_step(A, b, c, u, np.zeros(3), np.zeros(2), 0.2, 0.2)
print("one step from zero, tau = sigma = 0.2: x", np.round(x, 4), "y", np.round(y, 4))
for iterations in (10, 5000):
    x, y = solve(A, b, c, u, iterations)
    print(f"{iterations} iterations: x {np.round(x, 4)}, y {np.round(y, 4)}, cost {round(float(c @ x), 4)},"
          f" row error {round(float(np.max(np.abs(A @ x - b))), 6)}")

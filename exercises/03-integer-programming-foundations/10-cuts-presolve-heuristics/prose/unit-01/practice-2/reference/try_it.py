"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fractions import Fraction as F

from gomory import gomory_in_x

# Two rows: 3 x1 + x2 <= 8 and x1 + 2 x2 <= 6.
A = [[3, 1], [1, 2]]
b = [8, 6]

g, h = gomory_in_x([F(1), F(0), F(2, 5), F(-1, 5), F(11, 5)], A, b)
print("g for row [1, 0, 2/5, -1/5 | 11/5]:", [str(v) for v in g])
print("h for row [1, 0, 2/5, -1/5 | 11/5]:", h)
g, h = gomory_in_x([F(0), F(1), F(-1, 5), F(3, 5), F(7, 5)], A, b)
print("g for row [0, 1, -1/5, 3/5 | 7/5]:", [str(v) for v in g])
print("h for row [0, 1, -1/5, 3/5 | 7/5]:", h)

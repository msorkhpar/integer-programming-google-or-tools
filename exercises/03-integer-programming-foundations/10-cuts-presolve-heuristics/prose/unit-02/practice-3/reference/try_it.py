"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from tighten import tighten

# Crew rows over free binaries.
row = {"east": 7, "north": 2, "west": 3}
coefs, rhs = tighten(row, 8)
print("row 7e + 2n + 3w <= 8 becomes:", coefs, "<=", rhs)
print("row passed in afterwards:", row)
print("row 3x + 3y + 2z <= 7 becomes:", tighten({"x": 3, "y": 3, "z": 2}, 7))
print("row 2x + 5y <= 6 becomes:", tighten({"x": 2, "y": 5}, 6))

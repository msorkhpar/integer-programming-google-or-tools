"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from tiers import fits

# A tier caps (variables, rows, variables + rows) per kind of model; None is no cap.
tier = {"linear": (1500, 1000, 2200), "quadratic": (300, 1000, None)}
print("1200 vars, 800 rows, linear:", fits(1200, 800, False, tier))
print("1300 vars, 950 rows, linear:", fits(1300, 950, False, tier))
print("250 vars, 900 rows, quadratic:", fits(250, 900, True, tier))
print("400 vars, 900 rows, quadratic:", fits(400, 900, True, tier))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import math

from forecast import forecast

# objective 2400 at a budget of 800, price 1.5, range [600, 1000]
print("budget 900:", forecast(2400.0, 1.5, 800.0, 600.0, 1000.0, 900.0))
print("budget 650:", forecast(2400.0, 1.5, 800.0, 600.0, 1000.0, 650.0))
print("budget 1100:", forecast(2400.0, 1.5, 800.0, 600.0, 1000.0, 1100.0))
print("price -4, rhs 50 to 75, range [20, inf]:", forecast(900.0, -4.0, 50.0, 20.0, math.inf, 75.0))

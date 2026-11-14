"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fractional import fractional

lp = {"open_east": 1.0, "open_west": 0.35, "vans_east": 4.0000002, "vans_west": 2.75, "shift": -0.5}
print("LP values:", lp)
print("fractional names:", fractional(lp))
print("fractional names at tol 0.3:", fractional(lp, tol=0.3))

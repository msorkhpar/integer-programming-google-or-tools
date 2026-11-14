"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from most_fractional import most_fractional

print("open 0.85, crews 2.4, vans 1.0:", most_fractional({"open": 0.85, "crews": 2.4, "vans": 1.0}))
print("open 0.25, crews 1.75:", most_fractional({"open": 0.25, "crews": 1.75}))
print("open 1.0, crews 3.0000001:", most_fractional({"open": 1.0, "crews": 3.0000001}))

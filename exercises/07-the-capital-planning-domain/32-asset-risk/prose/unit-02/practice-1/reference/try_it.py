"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from gearbox import years_until

print("age 0, q 0.5, beta 2, eta 30:", round(years_until(0, 0.5, 2.0, 30.0), 3))
print("age 18, q 0.5, beta 2, eta 30:", round(years_until(18, 0.5, 2.0, 30.0), 3))
print("age 18, q 0.1, beta 2, eta 30:", round(years_until(18, 0.1, 2.0, 30.0), 3))
print("age 18, q 0.1, beta 1, eta 30:", round(years_until(18, 0.1, 1.0, 30.0), 3))

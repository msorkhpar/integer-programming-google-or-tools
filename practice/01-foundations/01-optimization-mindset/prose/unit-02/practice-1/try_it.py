"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from risk import pof_within

# A cable type with Weibull shape 3.0 and scale 50 years.
CABLE = dict(beta=3.0, eta=50.0)

print("age 30, next 1 year:", round(pof_within(age=30, years=1, **CABLE), 4))
print("age 30, next 5 years:", round(pof_within(age=30, years=5, **CABLE), 4))
print("age 60, next 5 years:", round(pof_within(age=60, years=5, **CABLE), 4))
print("age 45, next 0 years:", round(pof_within(age=45, years=0, **CABLE), 4))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from breakers import chance_of_none, failures_by_year

ages = [5, 18, 33]

print("ages 5, 18, 33 over 4 years:", [round(v, 4) for v in failures_by_year(ages, 3.0, 40.0, 4)])
print("one new breaker, first year:", [round(v, 6) for v in failures_by_year([0], 3.0, 40.0, 1)])
print("no failure for age 33 in 3 years:", round(chance_of_none(33, 3.0, 40.0, 3), 4))
print("no failure for age 5 in 3 years:", round(chance_of_none(5, 3.0, 40.0, 3), 4))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from bound import price_bound

# A clinic's LP: hours on scans, tests and visits, value per hour.
value = {"scans": 0.6, "tests": 0.4, "visits": 0.2}
rows = {
    "staff": ({"scans": 1, "tests": 1, "visits": 1}, 500),
    "scanner": ({"scans": 1}, 150),
}
print("prices staff 0.6, scanner 0:", price_bound(value, rows, {"staff": 0.6, "scanner": 0.0}))
print("prices staff 0.4, scanner 0.2:", price_bound(value, rows, {"staff": 0.4, "scanner": 0.2}))
print("prices staff 0.3, scanner 0.3:", price_bound(value, rows, {"staff": 0.3, "scanner": 0.3}))
print("prices staff 0.7, scanner -0.1:", price_bound(value, rows, {"staff": 0.7, "scanner": -0.1}))

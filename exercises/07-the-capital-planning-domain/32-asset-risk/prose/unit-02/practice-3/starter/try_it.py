"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from calibrate import scale_from_report

print("age 0, half fail within 14 years, beta 3:", round(scale_from_report(0, 14.0, 0.5, 3.0), 3))
print("age 0, 10% fail within 4 years, beta 3:", round(scale_from_report(0, 4.0, 0.1, 3.0), 3))
print("age 20, 10% fail within 4 years, beta 3:", round(scale_from_report(20, 4.0, 0.1, 3.0), 3))

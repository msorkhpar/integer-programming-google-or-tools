"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from start_table import npv_by_start_year

starts = (2030, 2031, 2032)

flat = npv_by_start_year((300, 200), 70, 10, starts, 2030, 0.0, 0.0)
print("0% rate, 0% escalation:", {y: round(v, 2) for y, v in flat.items()})
disc = npv_by_start_year((300, 200), 70, 10, starts, 2030, 0.05, 0.0)
print("5% rate, 0% escalation:", {y: round(v, 2) for y, v in disc.items()})
both = npv_by_start_year((300, 200), 70, 10, starts, 2030, 0.05, 0.03)
print("5% rate, 3% escalation:", {y: round(v, 2) for y, v in both.items()})

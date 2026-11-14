"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from budget_check import years_over

spend = {2045: 800.0000000002, 2046: 1210.0, 2044: 99.5, 2047: 4e-9}
budget = {2044: 100, 2045: 800, 2046: 1200, 2047: 0}
print("years over, spend", spend, ":", years_over(spend, budget))
print("years over with 2047 spend 0.3:", years_over({**spend, 2047: 0.3}, budget))

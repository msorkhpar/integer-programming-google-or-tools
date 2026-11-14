"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rebase import to_plan_date

entries = {2030: 650, 2031: 650, 2033: 610}

print("to 2030 at 4%:", {y: round(v, 3) for y, v in to_plan_date(entries, 0.04, 2030).items()})
print("to 2028 at 4%:", {y: round(v, 3) for y, v in to_plan_date(entries, 0.04, 2028).items()})
print("to 2032 at 4%:", {y: round(v, 3) for y, v in to_plan_date(entries, 0.04, 2032).items()})

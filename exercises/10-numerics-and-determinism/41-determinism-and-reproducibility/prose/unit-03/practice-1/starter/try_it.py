"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fleet import replacement_plan

ferries = {"F1": 310, "F2": 290, "F3": 300, "F4": 450, "F5": 280}

print("plan at budget 900:", replacement_plan(ferries, 900))
print("plan at budget 600:", replacement_plan(ferries, 600))
print("plan at budget 250:", replacement_plan(ferries, 250))

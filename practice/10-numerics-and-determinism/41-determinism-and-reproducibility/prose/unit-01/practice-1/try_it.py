"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fingerprint import fingerprint

plan = {"P02": 2031, "P09": 2030, "P14": 2032}

print("id of the plan:", fingerprint(plan))
print("id, same plan built backwards:", fingerprint(dict(reversed(list(plan.items())))))
print("id, P09 moved to 2031:", fingerprint({**plan, "P09": 2031}))

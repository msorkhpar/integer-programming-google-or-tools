"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from cases import CASES, check_request

print("cases in the table:", len(CASES))
for row, rule in CASES:
    print(f"case named {rule}: broken rules", check_request(row))

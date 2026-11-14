"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import math

from gaps import gap_report


def rounded(report):
    return {k: None if v is None else round(v, 4) for k, v in report.items()}


print("plan 450, bound 500:", rounded(gap_report(450.0, 500.0)))
print("plan 1200, bound 1150:", rounded(gap_report(1200.0, 1150.0)))
print("plan -30, bound -25:", rounded(gap_report(-30.0, -25.0)))
print("plan 0, bound 12:", rounded(gap_report(0.0, 12.0)))
print("no plan, bound 800:", rounded(gap_report(math.inf, 800.0)))

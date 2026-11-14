"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from change import value_change

# A library's LP swept over its staff hours: (from, to, price) segments.
sweep = [(0, 30, 4.0), (30, 60, 1.5), (60, 90, 0.25)]

print("from 40 by +10:", value_change(sweep, 40, 10))
print("from 40 by +30:", value_change(sweep, 40, 30))
print("from 40 by -20:", value_change(sweep, 40, -20))
print("from 40 by +60:", value_change(sweep, 40, 60))

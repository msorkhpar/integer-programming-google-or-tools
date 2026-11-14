"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from checker import broken_rules

# Each job is (days, installers, closures it must fit in or None).
jobs = {"wire": (2, 1, [(1, 4), (7, 10)]), "tile": (2, 2, None), "fit": (3, 1, None)}
print("wire 1, tile 0, fit 3:", broken_rules(jobs, {"wire": 1, "tile": 0, "fit": 3}, 3, 8))
print("wire 3, tile 0, fit 3:", broken_rules(jobs, {"wire": 3, "tile": 0, "fit": 3}, 3, 8))
print("wire 1, tile 1, fit 6:", broken_rules(jobs, {"wire": 1, "tile": 1, "fit": 6}, 3, 8))
print("wire 1, tile 1, fit 0, two installers:", broken_rules(jobs, {"wire": 1, "tile": 1, "fit": 0}, 2, 8))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from cs import cs_violations

# A brewery's day: batches of ale, lager and stout, profit per batch.
value = {"ale": 5, "lager": 4, "stout": 2}
rows = {
    "kettle": ({"ale": 1, "lager": 1, "stout": 1}, "<=", 12),
    "hops": ({"ale": 1}, "<=", 7),
}
prices = {"kettle": 4, "hops": 1}
print("plan 7/5/0:", cs_violations(value, rows, {"ale": 7, "lager": 5, "stout": 0}, prices))
print("plan 6/5/0:", cs_violations(value, rows, {"ale": 6, "lager": 5, "stout": 0}, prices))
print("plan 7/4/1:", cs_violations(value, rows, {"ale": 7, "lager": 4, "stout": 1}, prices))

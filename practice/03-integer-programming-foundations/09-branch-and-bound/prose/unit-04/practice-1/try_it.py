"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from bound import bound

# Four pumps a water utility could stock: (name, value, cost).
pumps = [("P1", 90, 30), ("P2", 80, 40), ("P3", 36, 36), ("P4", 20, 40)]

print("bound at budget 50, nothing fixed:", bound(pumps, 50, {}))
print("bound at budget 50, P1 at 0:", bound(pumps, 50, {"P1": 0}))
print("bound at budget 70, nothing fixed:", bound(pumps, 70, {}))
print("bound at budget 50, P2 and P3 at 1:", bound(pumps, 50, {"P2": 1, "P3": 1}))

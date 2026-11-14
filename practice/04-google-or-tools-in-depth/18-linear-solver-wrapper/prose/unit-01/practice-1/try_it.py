"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rows import best

# Rows are (name, lower or None, coefficients, upper or None); x0 and x1 run 0..10.
print("2 x0 + x1 <= 9, max 2 x0 + 3 x1:", best([("cap", None, {"x0": 2, "x1": 1}, 9)], {"x0": 2, "x1": 3}))
print("4 <= x0 + x1 <= 6, max x0 - x1:", best([("band", 4, {"x0": 1, "x1": 1}, 6)], {"x0": 1, "x1": -1}))
print("x0 - x1 >= 5, max -x0:", best([("lead", 5, {"x0": 1, "x1": -1}, None)], {"x0": -1}))
print("x0 + x1 <= 3 and x1 >= 5:", best([("cap", None, {"x0": 1, "x1": 1}, 3), ("floor", 5, {"x1": 1}, None)],
                                         {"x0": 1}))

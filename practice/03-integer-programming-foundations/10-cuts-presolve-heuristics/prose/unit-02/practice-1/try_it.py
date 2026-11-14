"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from reduce import reduce_row

# Inspection row over three free binaries u, v, w.
names = ("u", "v", "w")
lo, hi = dict.fromkeys(names, 0), dict.fromkeys(names, 1)

print("row 8u + 2v + 1w <= 5:", reduce_row({"u": 8, "v": 2, "w": 1}, 5, lo, hi))
print("row 1u + 2v + 1w <= 4:", reduce_row({"u": 1, "v": 2, "w": 1}, 4, lo, hi))
print("row 2u - 6v <= -3:", reduce_row({"u": 2, "v": -6}, -3, lo, hi))
print("row 3u + 2v <= 2, u fixed at 1:", reduce_row({"u": 3, "v": 2}, 2, {"u": 1, "v": 0}, {"u": 1, "v": 1}))

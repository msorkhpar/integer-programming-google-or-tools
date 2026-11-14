"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from deletion import deletion_filter

# Each rule is a (lower, upper) limit on one crane lift x, in tonnes.
limits = {"hook_max": (None, 8), "cargo_min": (12, None), "boom_max": (None, 10), "ground": (0, None)}


def feasible(subset):
    low = max([limits[r][0] for r in subset if limits[r][0] is not None], default=0)
    high = min([limits[r][1] for r in subset if limits[r][1] is not None], default=float("inf"))
    return low <= high


print("rules hook_max, cargo_min, boom_max, ground:", deletion_filter(list(limits), feasible))
print("rules boom_max, ground, cargo_min, hook_max:",
      deletion_filter(["boom_max", "ground", "cargo_min", "hook_max"], feasible))
print("rules hook_max, boom_max, ground:", deletion_filter(["hook_max", "boom_max", "ground"], feasible))

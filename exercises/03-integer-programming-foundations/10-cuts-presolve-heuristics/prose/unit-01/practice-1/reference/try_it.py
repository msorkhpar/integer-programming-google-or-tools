"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from cover import find_cover

# Inspection jobs (hours) competing for a 12-hour window.
hours = {"K1": 6, "K2": 5, "K3": 4, "K4": 2}
point = {"K1": 1, "K2": 1, "K3": 0.25, "K4": 0}

print("cover at window 12:", find_cover(hours, 12, point))
print("cover at window 12, K3 at 0:", find_cover(hours, 12, {**point, "K3": 0}))
print("cover at window 20:", find_cover(hours, 20, point))

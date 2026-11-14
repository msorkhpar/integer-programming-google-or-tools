"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from best import best_corners

hexagon = [(0.0, 0.0), (0.0, 3.0), (1.0, 4.0), (4.0, 4.0), (5.0, 2.0), (5.0, 0.0)]

print("max 1x + 1y:", best_corners(hexagon, (1, 1)))
print("max 2x + 1y:", best_corners(hexagon, (2, 1)))
print("min 1x - 1y:", best_corners(hexagon, (1, -1), "min"))
print("no corners:", best_corners([], (3, 2)))

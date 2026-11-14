"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from hull import supported_points

options = [(0, 12), (3, 10), (5, 9.5), (8, 7), (9, 3), (11, 0)]
asked = []


def best_for(s):
    asked.append(round(s, 4))
    return max(options, key=lambda p: (round(s * p[0] + (1 - s) * p[1], 9), p[0], p[1]))


print("supported points:", supported_points(best_for))
print("shares asked:", asked)

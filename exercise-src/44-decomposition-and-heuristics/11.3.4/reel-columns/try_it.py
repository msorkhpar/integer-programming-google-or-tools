"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from reel_columns import reel_columns

# Cable pieces as (length in metres, how many the jobs need), cut from 180 m reels.
pieces = {"trunk": (80, 5), "drop": (45, 8), "patch": (25, 7)}

lp, bounds, reels = reel_columns(pieces, 180)
print("LP optimum, 180 m reels:", round(lp, 3))
print("bound after each master solve:", [round(b, 3) for b in bounds])
print("reels in the integer plan:", reels)
print("reels for 'trunk' alone:", reel_columns({"trunk": (80, 5)}, 180)[2])

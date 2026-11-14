"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from reel_pricing import best_reel

# Pieces as (length in metres, how many the jobs need).
pieces = {"trunk": (80, 2), "drop": (45, 4), "patch": (25, 5)}

for prices in ({"trunk": 0.9, "drop": 0.3, "patch": 0.1},
               {"trunk": 0.2, "drop": 0.5, "patch": 0.3}):
    worth, pattern = best_reel(prices, pieces, 180)
    print(f"180 m reel at prices {prices}: worth {round(worth, 3)}, pattern {pattern}")
print("100 m reel, patch only at 0.4:", best_reel({"patch": 0.4}, {"patch": (25, 3)}, 100))

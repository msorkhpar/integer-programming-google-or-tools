"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from cuts import build, cut_table

# name -> (value, cost $k)
repairs = {"heating": (80, 55), "lift": (65, 40), "toilets": (35, 20), "paint": (20, 15), "fence": (15, 10)}
model, x, row = build(repairs, 120)

shares = [0.0, 0.25, 0.5]
for share, value in zip(shares, cut_table(model, row, shares)):
    print(f"best value at a {share:.0%} cut of 120:", round(value, 3))
print("budget limit afterwards:", row.upper_bound)

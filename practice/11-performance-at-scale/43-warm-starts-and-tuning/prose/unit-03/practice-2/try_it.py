"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from validation import folds, leaks

# Each orchard's survey model, one per season; seasons of one orchard share trees.
group_of = {
    "pear-spring": "pear", "pear-autumn": "pear",
    "plum-spring": "plum",
    "fig-spring": "fig", "fig-summer": "fig", "fig-autumn": "fig",
    "lime-summer": "lime",
}
names = list(group_of)

for k in (2, 3):
    print(f"folds with k={k}:", folds(names, group_of, k))
print("leaks, pear-spring+fig-summer vs pear-autumn:",
      leaks(["pear-spring", "fig-summer"], ["pear-autumn"], group_of))
print("leaks, plum-spring vs lime-summer:", leaks(["plum-spring"], ["lime-summer"], group_of))

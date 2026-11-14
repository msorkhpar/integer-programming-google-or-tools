"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from wildfire import go_until, upper_hull

plans = [(50, 1_000), (90, 970), (100, 930), (130, 900), (150, 820), (180, 700)]

print("supported plans:", upper_hull(plans))
for limit in (0.5, 1.0, 4.0, 10.0):
    print(f"price limit {limit}:", go_until(plans, limit))

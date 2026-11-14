"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from shares import share_range

buses = [(0, 12), (5, 10), (9, 6), (12, 0)]

for k, scores in enumerate(buses):
    print(f"candidate {k} {scores}:", share_range(buses, k))
print("candidate 1 of (0, 12), (5, 5), (12, 0):", share_range([(0, 12), (5, 5), (12, 0)], 1))

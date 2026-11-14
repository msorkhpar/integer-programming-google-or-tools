"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from depots import Upgrade, weighted_choice

stations = [Upgrade("Quay", 5, 350, 3000), Upgrade("Mill", 4, 120, 12000),
            Upgrade("Park", 3, 200, 1500), Upgrade("Dock", 2, 80, 6000)]

for price in (0, 15, 40):
    print(f"budget 8, {price} riders a tonne:", sorted(weighted_choice(stations, 8, price)))
print("budget 14, 15 riders a tonne:", sorted(weighted_choice(stations, 14, 15)))

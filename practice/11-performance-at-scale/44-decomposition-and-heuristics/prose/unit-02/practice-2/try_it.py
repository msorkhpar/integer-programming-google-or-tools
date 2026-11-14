"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from station_benders import benders

# Three candidate pumping stations for a town needing 120 units.
stations = {
    "ridge": {"build": 70, "capacity": 50, "energy": 2.2, "refill": 4},
    "pond": {"build": 120, "capacity": 90, "energy": 1.2, "refill": 6},
    "mill": {"build": 30, "capacity": 25, "energy": 3.5, "refill": 1},
}

for price in (7.0, 3.0):
    cost, plan, history = benders(stations, 120, 400, price)
    print(f"bought water at {price}: cost {round(cost, 2)}, plan {plan}")
    print(f"  (master value, best cost) per iteration at {price}:",
          [(round(lo, 1), round(up, 1)) for lo, up in history])

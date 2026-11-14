"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from refurbish import Station, refurbish

# Station(id, savings $k, cost $k, crew-days, required this year)
north = [
    Station("K1", 40, 35, 3),
    Station("K2", 28, 25, 4),
    Station("K3", 33, 30, 2),
    Station("K4", 10, 15, 1, must=True),
    Station("K5", 18, 20, 3),
]
print("budget 70, 20 crew-days, no pairs:", refurbish(north, budget=70, crew_days=20, bypass_pairs=[]))
print("budget 70, 20 crew-days, K2/K3 bypass:", refurbish(north, budget=70, crew_days=20, bypass_pairs=[("K2", "K3")]))
print("budget 100, 6 crew-days, no pairs:", refurbish(north, budget=100, crew_days=6, bypass_pairs=[]))

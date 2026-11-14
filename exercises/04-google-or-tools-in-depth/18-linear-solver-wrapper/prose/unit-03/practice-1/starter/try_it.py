"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from generators import most_delivered

# Generator units: yard stock, town needs, and route capacities.
stock = {"East yard": 8, "West yard": 6}
needs = {"Fen": 7, "Glen": 9}
routes = {("East yard", "Hub"): 6, ("Hub", "Fen"): 3, ("Hub", "Glen"): 5,
          ("East yard", "Fen"): 2, ("West yard", "Glen"): 4}
print("units delivered:", most_delivered(stock, needs, routes))
print("units delivered, Glen needs 2:", most_delivered(stock, dict(needs, Glen=2), routes))
print("units delivered, West yard holds 1:", most_delivered(dict(stock, **{"West yard": 1}), needs, routes))

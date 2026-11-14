"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from shipping import ship

# routes: (from, to) -> (cost per unit, capacity)
routes = {("East yard", "Fen"): (5, 8), ("East yard", "Hub"): (2, 8), ("West yard", "Hub"): (1, 8),
          ("West yard", "Glen"): (4, 8), ("Hub", "Fen"): (1, 6), ("Hub", "Glen"): (3, 6)}
print("stock 6+6, needs Fen 6, Glen 4:", ship({"East yard": 6, "West yard": 6}, {"Fen": 6, "Glen": 4}, routes))
print("stock 4+4, needs Fen 4, Glen 4:", ship({"East yard": 4, "West yard": 4}, {"Fen": 4, "Glen": 4}, routes))
print("stock 10+10, needs Fen 15, Glen 2:", ship({"East yard": 10, "West yard": 10}, {"Fen": 15, "Glen": 2}, routes))

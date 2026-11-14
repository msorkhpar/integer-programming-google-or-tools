"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

# Pyomo logs every set it builds and the whole solver log; keep its own logger to warnings.
logging.getLogger("pyomo").setLevel(logging.WARNING)

from prices import Unit, price

# Unit(MW when on, MW at most, $ per hour while on, $ per MWh)
fleet = {"wind": Unit(0, 40, 50, 2), "coal": Unit(50, 150, 1200, 25), "diesel": Unit(5, 40, 200, 90)}
for demand in (35, 120, 200):
    cost, unit_price = price(fleet, demand)
    print(f"demand {demand} MW: cost {round(cost, 2)}, price {round(unit_price, 2)}")

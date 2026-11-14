"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

# Pyomo logs every set it builds and the whole solver log; keep its own logger to warnings.
logging.getLogger("pyomo").setLevel(logging.WARNING)

from bounds import Asset, lp_bounds

# Asset(repair $k, replace $k, MVA after repair, MVA once new)
yard = {"K1": Asset(100, 380, 25, 55), "K2": Asset(70, 300, 20, 45), "K3": Asset(130, 450, 35, 70)}
for demand in (90, 130):
    big_m, hull = lp_bounds(yard, demand)
    print(f"demand {demand} MVA: big-M bound {round(big_m, 3)}, hull bound {round(hull, 3)}")

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from refurbish import Pump, plan, value_points

# Booster pumps: id, age, Weibull beta, eta, cost per failure, full refurbishment cost.
fleet = [Pump("K1", 25, 3.0, 35, 600, 450), Pump("K2", 45, 2.2, 55, 900, 500),
         Pump("K3", 18, 1.5, 40, 1500, 250)]

print("K1 values over 4 years:", [round(v, 1) for v in value_points(fleet[0], 4)])
print("K3 values over 4 years:", [round(v, 1) for v in value_points(fleet[2], 4)])
value, depths = plan(fleet, 600, 4)
print("value at fund 600:", round(value, 2))
print("depths at fund 600:", {k: round(d, 3) for k, d in depths.items()})

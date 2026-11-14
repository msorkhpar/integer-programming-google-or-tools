"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from crew_bound import crew_bound

hours = {2030: 30, 2031: 30}
builds = {
    "river bridge": {"value": {2030: 40, 2031: 35}, "hours": [20, 10], "must": False},
    "bus lane": {"value": {2030: 18, 2031: 21}, "hours": [15], "must": False},
    "fire station": {"value": {2031: 12}, "hours": [20], "must": True},
}

for price in (0.0, 0.5, 1.5):
    prices = {2030: price, 2031: price, 2032: price}
    bound, plan = crew_bound(builds, hours, prices)
    print(f"crew price {price}: bound {round(bound, 2)}, plan {plan}")

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from buses import buy_routes

# Offers are (seats, run by the city 0/1, price).
offers = [(20, 0, 80), (20, 1, 55), (40, 0, 130), (40, 1, 95), (60, 0, 180)]
routes = {"quay": 18, "college": 35, "airport": 52}
for limit in (0, 1, 2):
    total, plan = buy_routes(routes, offers, limit)
    print(f"city limit {limit}: total {total}, offers {plan}")

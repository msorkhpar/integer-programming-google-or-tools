"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from floor_prices import next_prices

floors = {2031: 80.0, 2032: 80.0, 2033: 80.0}
prices = {2031: 2.0, 2032: 2.0, 2033: 2.0}
veg_spend = {2031: 60.0, 2032: 95.0, 2033: 80.0}

print("bound 900, best 800:", next_prices(prices, floors, veg_spend, 900, 800, 1.0))
print("bound 820, best 800:", next_prices(prices, floors, veg_spend, 820, 800, 1.0))
print("bound 800, best 800:", next_prices(prices, floors, veg_spend, 800, 800, 1.0))

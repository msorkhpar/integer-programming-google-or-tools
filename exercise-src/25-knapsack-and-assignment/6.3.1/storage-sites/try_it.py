"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from storage import Site, cheapest_cover

# name, MWh, cost ($k)
sites = [Site("Oak", 5, 26), Site("Pine", 3, 14), Site("Elm", 6, 35), Site("Ash", 2, 11)]

print("need 8:", cheapest_cover(sites, 8))
print("need 11:", cheapest_cover(sites, 11))
print("need 0:", cheapest_cover(sites, 0))
print("need 17:", cheapest_cover(sites, 17))

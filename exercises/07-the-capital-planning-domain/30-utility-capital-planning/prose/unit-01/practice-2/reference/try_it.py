"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from envelopes import Request, oversubscribed, requested_by_year

reqs = [Request("P1", "pumps", 2030, (200, 100)), Request("P2", "pumps", 2031, (250,)),
        Request("R1", "reservoirs", 2030, (500, 500, 300))]
years = [2030, 2031, 2032]

table = requested_by_year(reqs, ["pumps", "reservoirs"], years)
print("pumps by year:", table["pumps"])
print("reservoirs by year:", table["reservoirs"])
envelopes = {("pumps", 2030): 300, ("pumps", 2031): 300, ("reservoirs", 2030): 450, ("reservoirs", 2032): 400}
print("over the envelopes:", oversubscribed(reqs, envelopes))

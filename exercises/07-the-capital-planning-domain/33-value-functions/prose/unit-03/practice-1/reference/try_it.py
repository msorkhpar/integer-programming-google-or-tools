"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from panel import panel_weights, price

votes = {"outages": [100, 90, 100, 100], "losses": [40, 70, 50], "savings": [30, 20, 35]}
reference = {"outages": 10, "losses": 300, "savings": 2_000}

w = panel_weights(votes)
print("weights:", {m: round(v, 4) for m, v in w.items()})
print("one outage in savings:", round(price(w, reference, "outages", "savings"), 3))
print("one unit of losses in savings:", round(price(w, reference, "losses", "savings"), 3))

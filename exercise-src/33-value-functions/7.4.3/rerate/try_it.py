"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from swings import price, rerate

old = {"delay": 500, "injuries": 4, "savings": 800}
ratings = {"delay": 100, "injuries": 70, "savings": 30}

new = rerate(ratings, old, {**old, "injuries": 2})
print("injuries swing 4 -> 2:", {m: round(r, 3) for m, r in new.items()})
other = {"delay": 1_000, "injuries": 4, "savings": 400}
again = rerate(ratings, old, other)
print("delay 1000, savings 400:", {m: round(r, 3) for m, r in again.items()})
print("delay in savings, old ratings:", round(price(ratings, old, "delay", "savings"), 4))
print("delay in savings, rerated:", round(price(again, other, "delay", "savings"), 4))

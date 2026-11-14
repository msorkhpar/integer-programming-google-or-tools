"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from bus import lifecycle_cost

print("price 700, running 45, 10 years, 0%, no extras:", round(lifecycle_cost(700, 45, 10, 0.0, {}, 0), 2))
print("same at 4%:", round(lifecycle_cost(700, 45, 10, 0.04, {}, 0), 2))
print("at 4%, overhaul 120 in year 5, resale 80:",
      round(lifecycle_cost(700, 45, 10, 0.04, {5: 120}, 80), 2))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import warnings

from valves import Valve, plan

warnings.simplefilter("ignore")      # PuLP's deprecation and objective warnings

# Valve(id, district, risk cut $k, cost $k, crew-weeks)
mains = [
    Valve("H7", "harbor", 26, 35, 2),
    Valve("H8", "harbor", 15, 20, 3),
    Valve("U5", "uptown", 30, 30, 4),
    Valve("U6", "uptown", 12, 10, 1),
]
print("budget 60, 6 weeks:", plan(mains, budget=60, crew_weeks=6, harbor_band=(0, 100), last_year={}))
print("budget 60, 6 weeks, harbor at least 50:", plan(mains, budget=60, crew_weeks=6, harbor_band=(50, 100), last_year={}))
print("budget 60, 6 weeks, H8 kept from last year:",
      plan(mains, budget=60, crew_weeks=6, harbor_band=(0, 100), last_year={"H8": 1.0, "U5": 0.0}))
print("budget 60, 6 weeks, H8 and U5 kept:",
      plan(mains, budget=60, crew_weeks=6, harbor_band=(0, 100), last_year={"H8": 1.0, "U5": 1.0}))

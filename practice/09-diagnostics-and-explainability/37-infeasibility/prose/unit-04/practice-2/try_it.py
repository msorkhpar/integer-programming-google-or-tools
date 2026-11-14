"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from port import fewest_refusals

days = {1: 1, 2: 1, 3: 1, 4: 1}
calm = {"Orion": (1, 4, 2), "Vega": (1, 4, 3), "Lyra": (3, 4, 4)}
busy = {"Orion": (1, 4, 2), "Vega": (1, 4, 2), "Lyra": (2, 4, 2)}

refused, schedule = fewest_refusals(calm, days)
print("refused, three different days asked:", refused)
print("schedule, three different days asked:", schedule)
refused, schedule = fewest_refusals(busy, days)
print("refused, all three ask for day 2:", refused)
print("schedule, all three ask for day 2:", schedule)

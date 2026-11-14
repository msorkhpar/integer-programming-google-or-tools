"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from choose import cheapest, present_cost, yearly_cost

options = {"reline": (900, 40, 25), "spot repair": (150, 110, 6), "replace": (2200, 10, 50)}

for name, (price, running, life) in options.items():
    print(f"{name} at 4%: present {present_cost(price, running, life, 0.04):.2f},"
          f" yearly {yearly_cost(price, running, life, 0.04):.2f}")
print("cheapest at 4%:", cheapest(options, 0.04))
print("cheapest at 0%:", cheapest(options, 0.0))

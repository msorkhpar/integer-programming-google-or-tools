"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from valuation import value_on

flows = {2030: -800, 2031: 250, 2033: 300, 2034: 350}

print("value on 2030 at 5%:", round(value_on(flows, 0.05, 2030), 3))
print("value on 2032 at 5%:", round(value_on(flows, 0.05, 2032), 3))
print("value on 2030 at 0%:", round(value_on(flows, 0.0, 2030), 3))

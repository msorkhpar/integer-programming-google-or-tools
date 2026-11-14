"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rates import revenue_requirement

years = [2030, 2031, 2032, 2033, 2034]
one = revenue_requirement({2030: 1_200}, 3, 0.08, {}, years)
print("1200 placed 2030, life 3, rate 8%:", {y: round(v, 2) for y, v in one.items()})
two = revenue_requirement({2030: 1_200, 2031: 600}, 3, 0.08, {2031: 50}, years)
print("plus 600 in 2031 and O&M 50 in 2031:", {y: round(v, 2) for y, v in two.items()})

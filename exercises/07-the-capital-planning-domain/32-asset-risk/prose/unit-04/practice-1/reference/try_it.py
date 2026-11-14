"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from refurb import Pump, yearly_cut

pump = Pump(30, 2.5, 35.0, 1.8, 55.0, 700.0)
years = list(range(2030, 2036))

print("start 2031, 1 year of work:", {y: round(v, 2) for y, v in yearly_cut(pump, years, 2031, 1).items()})
print("start 2031, 2 years of work:", {y: round(v, 2) for y, v in yearly_cut(pump, years, 2031, 2).items()})

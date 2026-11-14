"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from crossover import crossover_rate, npv

pump = [-800] + [130] * 12
liner = [-800] + [300] * 4

rate = crossover_rate(pump, liner)
print("crossover rate, pump vs liner:", round(rate, 6))
print("pump value at that rate:", round(npv(rate, pump), 3))
print("liner value at that rate:", round(npv(rate, liner), 3))
print("pump, liner value at 3%:", round(npv(0.03, pump), 2), round(npv(0.03, liner), 2))

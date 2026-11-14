"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pareto import dominates, unbeaten

routes = {"R1": (12, 3), "R2": (9, 6), "R3": (4, 11), "R4": (8, 5), "R5": (4, 10)}

print("R2 against R4, both max:", dominates(routes["R2"], routes["R4"], ("max", "max")))
print("unbeaten, both max:", sorted(unbeaten(routes, ("max", "max"))))
print("unbeaten, max then min:", sorted(unbeaten(routes, ("max", "min"))))

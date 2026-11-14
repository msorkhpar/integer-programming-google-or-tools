"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from tour import build, scaled

# A courier's depot and three drops, in km.
km = [
    [0, 2.4, 3.15, 1.8],
    [2.4, 0, 1.06, 2.9],
    [3.15, 1.06, 0, 2.25],
    [1.8, 2.9, 2.25, 0],
]
cost = scaled(km, 100)
print("km times 100:", cost)
print("km times 10:", scaled(km, 10))

for stops in ([1, 2, 3], [3, 2, 1], [2, 1, 3]):
    manager, routing = build(cost, 0)
    plan = routing.ReadAssignmentFromRoutes([stops], True)
    print(f"cost of tour 0 -> {stops} -> 0:", None if plan is None else plan.ObjectiveValue())

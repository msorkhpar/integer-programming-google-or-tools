"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from loads import build

# A bakery's two vans and four cafes.
distance = [
    [0, 4, 6, 3, 7],
    [4, 0, 2, 5, 6],
    [6, 2, 0, 4, 3],
    [3, 5, 4, 0, 5],
    [7, 6, 3, 5, 0],
]
trays = [0, 5, 3, 4, 2]
litres = [0, 20, 40, 10, 30]


def allowed(routes, demands, capacities):
    manager, routing = build(distance, 2, demands, capacities)
    return routing.ReadAssignmentFromRoutes(routes, True) is not None


print("trays only, caps 8 and 8, routes [1, 2] [3, 4]:", allowed([[1, 2], [3, 4]], {"trays": trays}, {"trays": [8, 8]}))
print("trays only, caps 7 and 8, routes [1, 2] [3, 4]:", allowed([[1, 2], [3, 4]], {"trays": trays}, {"trays": [7, 8]}))
both = {"trays": trays, "litres": litres}
print("trays and litres, litre caps 60 and 40:", allowed([[1, 2], [3, 4]], both, {"trays": [8, 8], "litres": [60, 40]}))
print("trays and litres, litre caps 50 and 40:", allowed([[1, 2], [3, 4]], both, {"trays": [8, 8], "litres": [50, 40]}))

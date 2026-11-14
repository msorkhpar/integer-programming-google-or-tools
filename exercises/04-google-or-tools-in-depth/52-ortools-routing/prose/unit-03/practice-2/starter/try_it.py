"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from overtime import build

# Two gardening crews and four parks, in minutes.
travel = [
    [0, 12, 18, 9, 20],
    [12, 0, 10, 15, 22],
    [18, 10, 0, 14, 8],
    [9, 15, 14, 0, 11],
    [20, 22, 8, 11, 0],
]
service = [0, 45, 30, 40, 25]


def cost(routes, finish_by, cost_per_minute):
    manager, routing = build(travel, service, finish_by, cost_per_minute)
    plan = routing.ReadAssignmentFromRoutes(routes, True)
    return None if plan is None else plan.ObjectiveValue()


routes = [[1, 2], [3, 4]]
print("routes [1, 2] [3, 4], back by 150 and 150, 4 per minute:", cost(routes, [150, 150], 4))
print("routes [1, 2] [3, 4], back by 100 and 150, 4 per minute:", cost(routes, [100, 150], 4))
print("routes [1, 2] [3, 4], back by 100 and 90, 4 per minute:", cost(routes, [100, 90], 4))
print("routes [1, 2] [3, 4], back by 100 and 90, 10 per minute:", cost(routes, [100, 90], 10))

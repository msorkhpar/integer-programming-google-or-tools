"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from handoff import build

# A removal firm's two vans: furniture collected at houses 1 and 2, dropped at stores 3 and 4.
distance = [
    [0, 4, 7, 6, 8],
    [4, 0, 5, 3, 9],
    [7, 5, 0, 8, 2],
    [6, 3, 8, 0, 6],
    [8, 9, 2, 6, 0],
]
pairs = [(1, 3), (2, 4)]


def allowed(routes):
    manager, routing = build(distance, 2, pairs)
    return routing.ReadAssignmentFromRoutes(routes, True) is not None


print("van 0 [1, 3], van 1 [2, 4]:", allowed([[1, 3], [2, 4]]))
print("van 0 [1, 2, 4, 3], van 1 []:", allowed([[1, 2, 4, 3], []]))
print("van 0 [3, 1], van 1 [2, 4]:", allowed([[3, 1], [2, 4]]))
print("van 0 [1, 4], van 1 [2, 3]:", allowed([[1, 4], [2, 3]]))

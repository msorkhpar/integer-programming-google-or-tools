"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from shifts import build

# A dog walker's van yard (0) and four parks, in minutes.
drive = [
    [0, 12, 18, 25, 9],
    [12, 0, 7, 20, 15],
    [18, 7, 0, 11, 22],
    [25, 20, 11, 0, 14],
    [9, 15, 22, 14, 0],
]


def allowed(shifts, routes):
    manager, routing = build(drive, shifts)
    return routing.ReadAssignmentFromRoutes(routes, True) is not None


print("shifts [45, 60], routes [1, 2] and [4, 3]:", allowed([45, 60], [[1, 2], [4, 3]]))
print("shifts [36, 60], routes [1, 2] and [4, 3]:", allowed([36, 60], [[1, 2], [4, 3]]))
print("shifts [45, 45], routes [1, 2] and [4, 3]:", allowed([45, 45], [[1, 2], [4, 3]]))
print("shifts [90, 30], routes [1, 2, 3, 4] and []:", allowed([90, 30], [[1, 2, 3, 4], []]))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from optional import build, skipped, solve

# A florist's two bikes and four orders; orders 2 and 4 may wait until tomorrow.
distance = [
    [0, 5, 8, 6, 9],
    [5, 0, 4, 7, 6],
    [8, 4, 0, 5, 3],
    [6, 7, 5, 0, 4],
    [9, 6, 3, 4, 0],
]
bouquets = [0, 3, 4, 3, 2]
penalties = {2: 40, 4: 15}

for bikes in ([6, 6], [4, 3], [8, 8]):
    manager, routing = build(distance, bouquets, bikes, penalties)
    solution = solve(routing)
    if solution is None:
        print(f"bikes carry {bikes}: no solution")
    else:
        print(f"bikes carry {bikes}: skipped {skipped(routing, manager, solution)}, cost {solution.ObjectiveValue()}")

manager, routing = build(distance, bouquets, [6, 6], penalties)
plan = routing.ReadAssignmentFromRoutes([[1, 3], [2]], True)
print("cost of routes [1, 3] [2] with 4 left off:", None if plan is None else plan.ObjectiveValue())

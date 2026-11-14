"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from warm import build, parameters, replan

# A print shop's two vans and five offices.
distance = [
    [0, 5, 8, 6, 9, 7],
    [5, 0, 4, 9, 6, 10],
    [8, 4, 0, 7, 3, 9],
    [6, 9, 7, 0, 8, 2],
    [9, 6, 3, 8, 0, 7],
    [7, 10, 9, 2, 7, 0],
]
boxes = [0, 2, 3, 4, 2, 3]

for vans, yesterday in (([8, 8], [[1, 3, 4], [2, 5]]), ([6, 8], [[1, 3, 4], [2, 5]])):
    manager, routing = build(distance, boxes, vans)
    start, solution = replan(routing, yesterday, parameters())
    print(f"vans {vans}, yesterday {yesterday}: yesterday's cost {start},"
          f" today's cost {None if solution is None else solution.ObjectiveValue()}")

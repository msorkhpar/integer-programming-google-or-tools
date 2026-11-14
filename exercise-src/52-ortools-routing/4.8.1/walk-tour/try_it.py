"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from walk import solve_tour

# A window cleaner's yard (0) and five houses, in minutes.
houses = [
    [0, 9, 14, 6, 11, 7],
    [9, 0, 5, 10, 13, 12],
    [14, 5, 0, 8, 4, 15],
    [6, 10, 8, 0, 5, 3],
    [11, 13, 4, 5, 0, 9],
    [7, 12, 15, 3, 9, 0],
]

tour, total = solve_tour(houses, 0)
print("tour from yard 0:", tour)
print("its total minutes:", total)
tour, total = solve_tour(houses, 3)
print("tour from house 3:", tour, "total:", total)

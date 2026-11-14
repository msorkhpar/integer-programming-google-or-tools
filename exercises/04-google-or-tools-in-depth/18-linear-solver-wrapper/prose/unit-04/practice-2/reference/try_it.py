"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from season import best_season

# Job values and lengths in months; one season of a given length.
print("values [7, 4, 5], months [3.25, 2.5, 4.0], season 7.25:", best_season([7, 4, 5], [3.25, 2.5, 4.0], 7.25))
print("same jobs, season 7.24:", best_season([7, 4, 5], [3.25, 2.5, 4.0], 7.24))
print("values [9, 2], months [8.01, 1.5], season 8.0:", best_season([9, 2], [8.01, 1.5], 8.0))

"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from crews import Job, best_order

# Culvert repairs: name, days, due day, cost per late day.
jobs = [Job("brook", 2, 3, 3), Job("lane", 4, 5, 1), Job("ford", 1, 1, 6), Job("weir", 3, 8, 2)]

print("four repairs:", best_order(jobs))
print("first two only:", best_order(jobs[:2]))
print("all due late:", best_order([Job("m1", 2, 20, 1), Job("m2", 3, 20, 1)]))

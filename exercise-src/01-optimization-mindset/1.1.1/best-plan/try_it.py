"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from best import Project, best_plan

# Five bridge repairs; B2 is ordered by the inspector.
bridges = [
    Project("B1", 70, 90),
    Project("B2", 50, 60, must_do=True),
    Project("B3", 40, 75),
    Project("B4", 30, 45, parent="B3"),
    Project("B5", 35, 50, group="deck"),
    Project("B6", 25, 38, group="deck"),
]

print("best plan at budget 200:", best_plan(bridges, 200))
print("best plan at budget 120:", best_plan(bridges, 120))
print("best plan at budget 40:", best_plan(bridges, 40))

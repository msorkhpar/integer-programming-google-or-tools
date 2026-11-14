"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from plans import Project, evaluate_plan

# Five pipe works; P1 is ordered by the regulator.
pipes = [
    Project("P1", 100, 130, must_do=True),
    Project("P2", 80, 110),
    Project("P3", 50, 70, parent="P2"),
    Project("P4", 60, 90, group="valves"),
    Project("P5", 40, 55, group="valves"),
]

print("plan P1+P2+P3 at budget 250:", evaluate_plan(pipes, 250, {"P1", "P2", "P3"}))
print("plan P1+P3 at budget 500:", evaluate_plan(pipes, 500, {"P1", "P3"}))
print("plan P2+P4+P5 at budget 500:", evaluate_plan(pipes, 500, {"P2", "P4", "P5"}))
print("plan P1+P2+P4 at budget 200:", evaluate_plan(pipes, 200, {"P1", "P2", "P4"}))

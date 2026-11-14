"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from inspections import Job, improve

# Five pump-station checks; 35 crew-hours in the week.
week = [Job("W1", "west", 40, 15), Job("W2", "west", 20, 10), Job("W3", "west", 15, 5),
        Job("E1", "east", 35, 15), Job("E2", "east", 10, 10)]
plan = {"W2", "E2"}
print("free west ->", sorted(improve(week, 35, plan, {"W1", "W2", "W3"})))
print("free east ->", sorted(improve(week, 35, plan, {"E1", "E2"})))
print("nothing free ->", sorted(improve(week, 35, plan, set())))

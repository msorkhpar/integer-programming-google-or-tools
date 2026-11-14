"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from week_lns import Job, lns

# Six pump-station checks; 40 crew-hours in the week.
week = [Job("W1", "west", 45, 15), Job("W2", "west", 35, 10), Job("C1", "centre", 30, 10),
        Job("C2", "centre", 15, 5), Job("H1", "harbour", 40, 20), Job("H2", "harbour", 10, 5)]
start = {"W1", "C2", "H2"}
west, centre, harbour = {"W1", "W2"}, {"C1", "C2"}, {"H1", "H2"}

plan, history = lns(week, 40, start, [harbour, west, centre])
print("rounds harbour, west, centre -> history:", history)
print("final plan:", sorted(plan))
plan, history = lns(week, 40, start, [])
print("no rounds -> history:", history, "plan:", sorted(plan))

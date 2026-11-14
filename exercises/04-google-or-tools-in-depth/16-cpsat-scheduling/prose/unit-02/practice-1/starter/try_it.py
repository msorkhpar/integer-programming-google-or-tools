"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from paving import paving_plan

# Each job is (days, gangs it needs).
jobs = {"birch": (3, 2), "maple": (2, 1), "pine": (4, 1), "cedar": (1, 3)}
print("plan with 3 gangs:", paving_plan(jobs, 3, 15))
print("plan with 4 gangs:", paving_plan(jobs, 4, 15))
print("plan with 2 gangs:", paving_plan(jobs, 2, 15))

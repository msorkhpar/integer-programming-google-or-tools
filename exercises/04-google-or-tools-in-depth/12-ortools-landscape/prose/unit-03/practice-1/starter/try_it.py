"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from chooser import Problem, choose_api

print("delivery routes with time windows:", choose_api(Problem(routes=True, intervals=True)))
print("plain flow:", choose_api(Problem(shape="flow")))
print("knapsack with a side rule:", choose_api(Problem(shape="knapsack", side_rules=True)))
print("shift plan with no-overlap tasks:", choose_api(Problem(intervals=True)))
print("blend with fractional tonnes:", choose_api(Problem(continuous=True, logic=True)))
print("nothing special:", choose_api(Problem()))

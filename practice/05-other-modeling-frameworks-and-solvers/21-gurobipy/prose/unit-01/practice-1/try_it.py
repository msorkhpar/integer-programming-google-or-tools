"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from gurobipy import GRB

from outcome import outcome

print("OPTIMAL with 2 solutions:", outcome(GRB.OPTIMAL, 2))
print("TIME_LIMIT with 5 solutions:", outcome(GRB.TIME_LIMIT, 5))
print("SOLUTION_LIMIT with 0 solutions:", outcome(GRB.SOLUTION_LIMIT, 0))
print("INFEASIBLE with 0 solutions:", outcome(GRB.INFEASIBLE, 0))
print("INF_OR_UNBD with 0 solutions:", outcome(GRB.INF_OR_UNBD, 0))
print("CUTOFF with 0 solutions:", outcome(GRB.CUTOFF, 0))

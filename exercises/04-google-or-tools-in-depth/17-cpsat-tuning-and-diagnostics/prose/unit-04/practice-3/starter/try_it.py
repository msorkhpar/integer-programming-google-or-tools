"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from summary import read_summary, relative_gap

# A made-up summary of a van-routing model, shaped like CP-SAT's.
log = ("#Done    0.80s main\n\nCpSolverResponse summary:\nstatus: FEASIBLE\nobjective: 1250\n"
       "best_bound: 1190\nbooleans: 44\nconflicts: 87\nbranches: 1502\nwalltime: 0.81\n")
fields = read_summary(log)
print("fields read:", fields)
print("gap at objective 1250, bound 1190:", round(relative_gap(log), 4))
print("gap at objective 0, bound 2:", relative_gap(log.replace("1250", "0").replace("1190", "2")))

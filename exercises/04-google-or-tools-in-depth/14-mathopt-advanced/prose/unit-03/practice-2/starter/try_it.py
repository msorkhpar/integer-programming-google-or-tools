"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from verdict import hint_verdict

print("HIGHS, start feasible:", hint_verdict("HIGHS", ["Presolving", "MIP start solution is feasible, objective value is 77"]))
print("HIGHS, start refused:", hint_verdict("HIGHS", ["User-supplied values of discrete variables cannot yield feasible solution"]))
print("CP_SAT, hint incomplete:", hint_verdict("CP_SAT", ["The solution hint is incomplete: 2 out of 9 non fixed variables hinted."]))
print("CP_SAT, hint infeasible:", hint_verdict("CP_SAT", ["The solution hint is complete, but it is infeasible! we will try to repair it."]))
print("GSCIP, storage line:", hint_verdict("GSCIP", ["2/2 feasible solution given by solution candidate storage, new primal bound 7.7e+01"]))
print("GSCIP, no hint lines:", hint_verdict("GSCIP", ["presolving:", "SCIP Status: problem is solved"]))

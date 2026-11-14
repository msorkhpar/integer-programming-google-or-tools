"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from backend import pick_backend

print("prefs GUROBI, HIGHS, CBC:", pick_backend(["GUROBI", "HIGHS", "CBC"]))
print("prefs PDLP, SCIP:", pick_backend(["PDLP", "SCIP"]))
print("prefs GLOP, CLP:", pick_backend(["GLOP", "CLP"]))
print("prefs CPLEX:", pick_backend(["CPLEX"]))

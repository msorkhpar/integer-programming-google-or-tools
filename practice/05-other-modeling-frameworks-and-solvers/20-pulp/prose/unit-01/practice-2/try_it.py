"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import pulp

from verdict import report


def library_problem(vans):
    """A library service's branch refits: maximize books added with `vans` delivery vans."""
    prob = pulp.LpProblem("branches", pulp.LpMaximize)
    b = {k: prob.add_variable(f"b_{k}", 0, 1, cat=pulp.LpBinary) for k in ("mill", "dock", "park")}
    prob += 500 * b["mill"] + 350 * b["dock"] + 200 * b["park"], "books"
    prob += 3 * b["mill"] + 2 * b["dock"] + 1 * b["park"] <= vans, "vans"
    return prob, b


prob, b = library_problem(vans=4)
prob.solve(pulp.PULP_CBC_CMD(msg=False))
print("vans 4, search finished:", report(prob))
prob.sol_status = pulp.LpSolutionIntegerFeasible
print("vans 4, read as stopped by a limit:", report(prob))
prob, b = library_problem(vans=4)
prob += b["mill"] + b["dock"] >= 2, "both"
prob.solve(pulp.PULP_CBC_CMD(msg=False))
print("vans 4, mill and dock both required:", report(prob))

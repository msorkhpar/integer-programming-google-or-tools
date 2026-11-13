"""What PuLP 3.3's two status codes say: a full CBC solve, one stopped after one node, one stopped by a
time limit, and one with no plan."""

import pulp

from gridcap import generate
from pulp_timing import build, cbc

print("LpStatus:  ", pulp.LpStatus)
print("LpSolution:", pulp.LpSolution)

small = generate("small")
for label, options in (("no limit", {}), ("maxNodes=1", {"maxNodes": 1})):
    pt = build(small)
    status = pt.prob.solve(cbc(**options))
    print(f"{label:<11} status {status} {pulp.LpStatus[status]:<8} sol_status {pt.prob.sol_status} "
          f"{pulp.LpSolution[pt.prob.sol_status]:<22} NPV ${pulp.value(pt.prob.objective):,.0f}k")

pt = build(generate("medium"))
status = pt.prob.solve(cbc(timeLimit=2))
print(f"medium, timeLimit=2: status {status} {pulp.LpStatus[status]}, sol_status {pt.prob.sol_status} "
      f"{pulp.LpSolution[pt.prob.sol_status]}")

infeasible = generate("small")
pt = build(infeasible)
pt.prob += pt.x["P001", 2028] + pt.x["P001", 2029] >= 2, "twice_P001"    # a start the once row forbids
status = pt.prob.solve(cbc())
print(f"forced     status {status} {pulp.LpStatus[status]:<8} sol_status {pt.prob.sol_status} "
      f"{pulp.LpSolution[pt.prob.sol_status]}")

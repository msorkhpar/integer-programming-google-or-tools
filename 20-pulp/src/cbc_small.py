"""Solve lesson 6.4.1's model on GridCap small with PuLP and CBC, and read the schedule."""

import pulp

from gridcap import generate
from pulp_timing import build, cbc, schedule

small = generate("small")
pt = build(small)
status = pt.prob.solve(cbc(gapRel=0))
print("status", status, pulp.LpStatus[status], "| sol_status", pt.prob.sol_status,
      pulp.LpSolution[pt.prob.sol_status])
print(f"NPV ${pulp.value(pt.prob.objective):,.0f}k")
plan = schedule(pt)
late = {pid: t for pid, t in plan.items() if t > small.project(pid).earliest_start}
print(f"started {len(plan)} of {len(small.projects)}; {len(late)} later than their earliest year")
for pid, t in sorted(late.items()):
    p = small.project(pid)
    print(f"  {pid} window {p.earliest_start}-{p.latest_start} starts {t}  NPV {p.npv[p.earliest_start]:,} -> {p.npv[t]:,}")
spend = {y: sum(small.project(pid).spend(t).get(y, 0) for pid, t in plan.items()) for y in small.years}
print("spend / budget:", ", ".join(f"{y} {spend[y]:,}/{small.budget[y]:,}" for y in small.years))
row = pt.prob.get_constraint_by_name("budget_2027")
print("budget_2027 slack", row.slack, "| P008 starts:",
      {t: pt.x["P008", t].varValue for t in small.project("P008").starts()})

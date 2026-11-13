"""Lesson 14.2.5: the NPV-risk frontier of GridCap small (a fictional utility's portfolio).

steps/05: five epsilon-constraint points between the plan with the most NPV and the plan that
removes the most risk, each finished by a lexicographic second solve.
"""

from export import gridcap_export
from steps import use

raw = gridcap_export("small")
cipt = use(5)
request = cipt.data.load_request(raw)
points = cipt.goals.frontier(request, points=5)
print("frontier of GridCap small, five points requested:")
print("   NPV ($k)   risk removed ($k)   funded   NPV given up per $k of risk")
for before, p in zip([None] + points, points):
    rate = "" if before is None else f"{(before.npv - p.npv) / (p.risk - before.risk):.2f}"
    print(f"{p.npv:>11,.0f}   {p.risk:>17,.1f}   {len(p.plan.starts):>6}   {rate:>27}")

weighted = []
for w in (0.0, 0.5, 1.0, 2.0, 5.0, 100.0):
    built = cipt.model.build(request)
    built.model.maximize(built.npv + w * built.risk)
    plan = cipt.solve.solve_built(built)
    weighted.append(f"{w:g} -> ({plan.npv:,.0f}, {plan.risk:,.1f})")
print("weighted sum NPV + w * risk, w -> (NPV, risk): " + "; ".join(weighted[:3]))
print("  " + "; ".join(weighted[3:]))

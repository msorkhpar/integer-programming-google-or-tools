"""A sweep of ε finds one plan per floor at most: compare grids of 5, 11 and 21 floors with every Pareto plan."""

from frontier import epsilon_constraint, exact_frontier, grid, payoff_table, supported
from gridcap import generate
from objectives import build

small = generate("small")
two = build(small)

# Every Pareto-optimal plan, as (NPV, risk). Lesson 8.3.2 explains how exact_frontier finds them.
found, _ = exact_frontier(two.model, two.risk, two.npv)
pareto = {(round(p.second), round(p.first, 3)) for p in found}
hull = {(round(p.second), round(p.first, 3)) for p in supported(found)}
print(f"Pareto-optimal plans: {len(pareto)}, of which a weighted sum reaches {len(hull)}")

npv_plan, risk_plan = payoff_table(two.model, two.npv, two.risk)
for n in (5, 11, 21):
    floors = grid(npv_plan.second, risk_plan.second, n)          # risk floors, both ends included
    points = set()
    for floor in floors:
        p = epsilon_constraint(two.model, two.npv, two.risk, floor)
        points.add((round(p.first), round(p.second, 3)))
    print(f"{n:2} floors: {len(points):2} different plans, {len(points & pareto):2} Pareto-optimal, "
          f"{len(points - hull):2} unsupported (no weighted sum finds them)")

risks = sorted(r for _, r in pareto)
gap = min(b - a for a, b in zip(risks, risks[1:]))
print(f"closest neighbours on the frontier differ by ${gap * 1000:,.0f} of risk; a risk grid that cannot "
      f"miss a plan needs {int((risks[-1] - risks[0]) / gap) + 1:,} floors")

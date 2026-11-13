"""Lesson 6.3.2: the LP relaxation of the crew assignment splits projects between crews.

GridCap, its crews and their qualifications are fictional.
"""

from gridcap import generate
from knapsack_models import EXACT, assignment_model, base_plan, solve_highs

small = generate("small")
plan = base_plan(small)
model, x = assignment_model(plan, only_eligible=True)
whole = solve_highs(model, EXACT).objective_value()
model, x = assignment_model(plan, only_eligible=True, integer=False)
result = solve_highs(model)
print(f"whole crews: ${whole:,.0f}k; LP relaxation: ${result.objective_value():,.2f}k "
      f"({(whole - result.objective_value()) / whole:.1%} below)")
shares: dict[str, list[str]] = {}
for (i, k), var in x.items():
    value = result.variable_values(var)
    if value > 1e-6:
        shares.setdefault(i, []).append(f"{k} {value:.3f}")
split = {i: s for i, s in shares.items() if len(s) > 1}
print(f"{len(split)} of {len(plan)} projects split between crews:")
for i, s in split.items():
    print(f"  {i}: {', '.join(s)}")

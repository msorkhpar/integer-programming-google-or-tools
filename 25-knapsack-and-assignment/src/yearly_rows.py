"""Lesson 6.3.1: each year's budget is one more capacity row, so the selection becomes a multi-dimensional knapsack.

Every project starts as early as it can and spends its cost profile from that year on. GridCap is a
fictional utility's portfolio.
"""

from gridcap import generate
from knapsack_models import EXACT, capital_row, chosen, discretionary, knapsack_model, solve_highs, year_rows

small = generate("small")
values = {p.project_id: p.value for p in discretionary(small)}
rows = [capital_row(small)] + year_rows(small)

for label, use in (("capital row only", rows[:1]), ("capital and 5 yearly rows", rows)):
    model, x = knapsack_model(values, use)
    result = solve_highs(model, EXACT)
    plan = chosen(x, result)
    print(f"{label}: {len(plan)} projects, value ${result.objective_value():,.0f}k")

print("row          uses     left   slack")
for row in rows:
    used = sum(row.weight.get(i, 0) for i in plan)
    print(f"{row.name:<11} {used:6,} {row.capacity:8,} {row.capacity - used:7,}")

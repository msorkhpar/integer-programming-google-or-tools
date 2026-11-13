"""Lesson 6.3.1: dynamic programming finds the best plan of a one-row knapsack with whole-number costs.

The table of lesson 3.1.3 counted plans; this one keeps the best value for every budget amount.
GridCap is a fictional utility's portfolio.
"""

import math

from gridcap import generate
from knapsack_models import EXACT, capital_row, chosen, discretionary, knapsack_model, solve_highs, year_rows


def best_plan(items: list[tuple[str, int, int]], budget: int):
    """items are (name, value, cost) with whole-number costs. Returns best[0..budget] and one best plan."""
    best = [0] * (budget + 1)       # best[b]: the most value the items seen so far give within b
    took = []                       # took[k][b]: item k is in the best plan for budget b
    for name, value, cost in items:
        row = [False] * (budget + 1)
        for b in range(budget, cost - 1, -1):           # downward, so each item is used at most once
            if best[b - cost] + value > best[b]:
                best[b] = best[b - cost] + value
                row[b] = True
        took.append(row)
    plan, b = [], budget
    for (name, value, cost), row in zip(reversed(items), reversed(took)):
        if row[b]:                                      # item k was taken for budget b: undo it
            plan.append(name)
            b -= cost
    return best, plan[::-1]


small = generate("small")
capital = capital_row(small)
unit = math.gcd(*capital.weight.values(), capital.capacity)       # every amount is a multiple of $10k
items = [(p.project_id, p.value, p.capex // unit) for p in discretionary(small)]
best, plan = best_plan(items, capital.capacity // unit)

print(f"unit ${unit}k; table of {len(items)} items x {capital.capacity // unit + 1:,} budget steps")
print(f"best value ${best[-1]:,}k with {len(plan)} projects: {' '.join(plan)}")
model, x = knapsack_model({p.project_id: p.value for p in discretionary(small)}, [capital])
result = solve_highs(model, EXACT)
print(f"HiGHS: ${result.objective_value():,.0f}k, same plan: {chosen(x, result) == plan}")
print("the same table answers every smaller budget:")
for budget in (20_000, 25_000, 28_000, 30_000, capital.capacity):
    print(f"  ${budget:,}k -> ${best[budget // unit]:,}k")

rows = [capital] + year_rows(small)
cells = math.prod(row.capacity // unit + 1 for row in rows)
print(f"with all {len(rows)} rows the table needs one axis per row: {cells:.2e} cells per item")

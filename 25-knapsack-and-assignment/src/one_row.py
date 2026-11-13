"""Lesson 6.3.1: GridCap small's budget-only selection is a 0-1 knapsack, and its plan ignores the yearly budgets.

GridCap is a fictional utility's portfolio. Must-do projects are paid for first, as in lesson 3.2.4.
"""

from gridcap import generate
from knapsack_models import EXACT, capital_row, chosen, discretionary, knapsack_model, solve_highs, year_rows

small = generate("small")
values = {p.project_id: p.value for p in discretionary(small)}
capital = capital_row(small)
model, x = knapsack_model(values, [capital])
result = solve_highs(model, EXACT)
plan = chosen(x, result)

print(f"{len(values)} discretionary projects compete for ${capital.capacity:,}k")
print(f"best plan: {len(plan)} projects, value ${result.objective_value():,.0f}k, "
      f"capex ${sum(capital.weight[i] for i in plan):,}k")
for row in year_rows(small):
    used = sum(row.weight.get(i, 0) for i in plan)
    flag = "  over" if used > row.capacity else ""
    print(f"  {row.name}: the plan spends ${used:,}k of ${row.capacity:,}k left{flag}")

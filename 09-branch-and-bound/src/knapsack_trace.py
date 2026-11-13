"""Lesson 3.2.4: every node of the knapsack search on the tiny portfolio."""

from gridcap import generate
from knapsack import by_ratio, gridcap_knapsack, solve

items, budget, must = gridcap_knapsack(generate("tiny"))
print(f"budget ${budget:,}k after must-do {', '.join(must)}; ratio order:")
for it in by_ratio(items):
    print(f"  {it.name}  value {it.value:>5,}  cost {it.cost:>5,}  ratio {it.value / it.cost:.3f}")
log: list[str] = []
result = solve(items, budget, log)
print("\n".join(log))
print(f"best {result.value:,}: {', '.join(result.plan)}")

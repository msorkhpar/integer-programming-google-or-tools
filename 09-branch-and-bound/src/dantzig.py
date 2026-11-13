"""Lesson 3.2.4: Dantzig's bound on the small budget-only knapsack, checked against GLOP's LP relaxation."""

from gridcap import generate
from knapsack import by_ratio, dantzig_bound, gridcap_knapsack
from selection import knapsack_model, solve_lp

items, budget, must = gridcap_knapsack(generate("small"))
print(f"must-do {', '.join(must)} funded first; {len(items)} projects compete for ${budget:,}k")
order = by_ratio(items)
left = budget
for it in order[:3]:
    left -= it.cost
    print(f"  {it.name}  value {it.value:>5,}  cost {it.cost:>5,}  ratio {it.value / it.cost:.3f}  budget left {left:>6,}")
print("  ...")

lp = dantzig_bound(order, budget, fixed={})
whole = [n for n, v in lp.taken.items() if v == 1.0]
split = next(it for it in order if it.name == lp.split)
print(f"{len(whole)} projects fit whole; {split.name} (cost {split.cost:,}) fits {lp.taken[split.name]:.3f} of the way")
print(f"Dantzig's bound: {lp.value:,.3f}")

sel = knapsack_model(items, budget, integer=False)
for fixed in ({}, {lp.split: 0}, {lp.split: 1}):
    glop = solve_lp(sel, fixed)
    ours = dantzig_bound(order, budget, fixed)
    print(f"fixed {str(fixed):<13} Dantzig {ours.value:>10,.3f}   GLOP {glop.value:>10,.3f}")

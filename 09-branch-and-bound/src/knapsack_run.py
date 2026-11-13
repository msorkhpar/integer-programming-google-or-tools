"""Lesson 3.2.4: the knapsack branch-and-bound on three GridCap sizes, checked against brute force and HiGHS."""

from gridcap import generate
from knapsack import brute_force, by_ratio, dantzig_bound, gridcap_knapsack, solve
from selection import knapsack_model, solve_milp

for size in ("tiny", "small", "medium"):
    items, budget, must = gridcap_knapsack(generate(size))
    result = solve(items, budget)
    check = (f"brute force {brute_force(items, budget):,}" if len(items) <= 20
             else f"HiGHS {solve_milp(knapsack_model(items, budget)).objective_value():,.0f}")
    print(f"{size:<6} {len(items):>3} projects  ours {result.value:>7,} in {result.nodes:>3} nodes   {check}")
    root = dantzig_bound(by_ratio(items), budget, {}).value
    print(f"       root bound {root:,.2f}; pruned: {result.pruned}")

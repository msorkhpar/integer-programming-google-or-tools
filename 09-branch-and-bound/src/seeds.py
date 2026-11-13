"""Lesson 3.2.4: twenty more small portfolios, one per seed, each solved by our search and by HiGHS."""

from gridcap import generate
from knapsack import gridcap_knapsack, solve
from selection import knapsack_model, solve_milp

nodes, agree = [], 0
for seed in range(1, 21):
    items, budget, _ = gridcap_knapsack(generate("small", seed))
    ours = solve(items, budget)
    highs = solve_milp(knapsack_model(items, budget)).objective_value()
    agree += abs(ours.value - highs) < 1e-6
    nodes.append(ours.nodes)
print(f"{agree} of 20 seeds agree with HiGHS; nodes per search from {min(nodes)} to {max(nodes):,}")
print("nodes by seed:", " ".join(str(n) for n in nodes))

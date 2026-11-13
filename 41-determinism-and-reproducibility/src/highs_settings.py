"""Lesson 10.2.2, HiGHS: what its seed and thread count change on a run stopped by a node limit.

GridCap medium (a fictional portfolio), stopped after 300 branch-and-bound nodes. Every run is a
fresh process, because HiGHS fixes its thread count at the first solve of a process (lesson 4.2.4).
"""

from repeat import repeat, summary

FIELDS = ["result.objective", "result.bound", "result.plan_digest", "result.stats.simplex_iterations"]
base = {"size": "medium", "objective": "npv", "solver": "highs"}

for seed in [1, 2, 3]:
    config = {**base, "params": {"node_limit": 300, "random_seed": seed}}
    summary(f"HiGHS, node limit 300, random_seed {seed}", repeat(config, 2), FIELDS)
for threads in [1, 4]:
    config = {**base, "params": {"node_limit": 300, "random_seed": 1, "highs_threads": threads}}
    summary(f"HiGHS, node limit 300, random_seed 1, threads {threads}", repeat(config, 2), FIELDS)

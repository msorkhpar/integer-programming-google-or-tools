"""Lesson 10.2.2, SCIP through MathOpt: one thread, a seed that picks among tied plans, a node limit.

GridCap small and medium (a fictional portfolio). Every run is a fresh process.
"""

from repeat import repeat, summary

FIELDS = ["result.objective", "result.plan_digest", "result.stats.nodes", "result.stats.simplex_iterations"]
summary("SCIP, highest NPV, random_seed 5, GridCap small",
        repeat({"size": "small", "objective": "npv", "solver": "scip", "params": {"random_seed": 5}}, 3), FIELDS)
for seed in [1, 4]:
    config = {"size": "small", "objective": "count", "solver": "scip",
              "params": {"random_seed": seed, "relative_gap_tolerance": 0.0}}
    summary(f"SCIP, most projects, random_seed {seed}, GridCap small", repeat(config, 2), FIELDS[:2])
for seed in [1, 2]:
    config = {"size": "medium", "objective": "npv", "solver": "scip", "params": {"random_seed": seed, "node_limit": 200}}
    summary(f"SCIP, node limit 200, random_seed {seed}, GridCap medium", repeat(config, 2),
            ["result.objective", "result.bound", "result.plan_digest"])

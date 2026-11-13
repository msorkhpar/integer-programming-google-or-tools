"""Lesson 10.2.1: the three sources of a different answer, each shown by rerunning one config.

Every run is a fresh process (repeat.py) solving a GridCap model; for each field the program prints
its value when all runs agreed and `differs` when they did not. GridCap is a fictional utility's
portfolio. The page quotes only lines that came out the same way on every run of this program.
"""

from repeat import repeat, summary

PLAN = ["result.status", "result.objective", "result.plan_digest"]

# 1. Threads: CP-SAT's parallel workers race (lesson 4.6.3 measured 8 workers).
threads = {"size": "medium", "objective": "npv", "solver": "cpsat",
           "params": {"num_workers": 4, "random_seed": 7, "max_deterministic_time": 2.0}}
summary("CP-SAT, 4 workers, seed 7, deterministic limit 2, GridCap medium", repeat(threads, 5), PLAN)

# 2. Time limits: HiGHS stopped by the clock, then by a count of nodes.
clock = {"size": "medium", "objective": "npv", "solver": "highs", "params": {"time_limit": 3.0}}
# Only these two fields: whether the plan also differs depends on where the clock stopped each run.
summary("HiGHS, time limit 3 s, GridCap medium", repeat(clock, 3),
        ["result.status", "result.stats.simplex_iterations"])
nodes = {"size": "medium", "objective": "npv", "solver": "highs", "params": {"node_limit": 300}}
summary("HiGHS, node limit 300, GridCap medium", repeat(nodes, 3),
        PLAN + ["result.stats.simplex_iterations", "result.stats.nodes"])

# 3. Ties: many plans fund the most projects; the order of a set decides which one comes back.
for solver, params in [("highs", {"relative_gap_tolerance": 0.0}),
                       ("cpsat", {"num_workers": 1, "random_seed": 7})]:
    for order in ["given", "set"]:
        ties = {"size": "small", "objective": "count", "order": order, "solver": solver, "params": params}
        summary(f"{solver}, most projects, projects in {order} order, GridCap small", repeat(ties, 4), PLAN)

# The same set order on the NPV question, which has one best plan on GridCap small.
npv = {"size": "small", "objective": "npv", "order": "set", "solver": "highs", "params": {"relative_gap_tolerance": 0.0}}
summary("highs, highest NPV, projects in set order, GridCap small", repeat(npv, 4), PLAN)

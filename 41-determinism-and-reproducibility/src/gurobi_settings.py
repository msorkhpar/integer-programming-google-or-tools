"""Lesson 10.2.2, Gurobi: deterministic by default for a fixed thread count; Method=2 is barrier.

GridCap medium (a fictional portfolio, 887 binaries, inside the size-limited license) solved in a
fresh process per run. Every environment is quiet, and only numbers are printed from Gurobi: its
messages can name the machine and the license holder. Without a license each run reports NO_LICENSE.
"""

from repeat import repeat, summary

FIELDS = ["result.status", "result.objective", "result.plan_digest", "result.stats.nodes",
          "result.stats.work", "result.stats.fingerprint"]
base = {"size": "medium", "objective": "npv", "solver": "gurobi"}
for label, params in [("default parameters", {}),
                      ("Threads=1", {"Threads": 1}),
                      ("Threads=4", {"Threads": 4}),
                      ("Method=2", {"Method": 2}),
                      ("WorkLimit=0.2", {"WorkLimit": 0.2}),
                      ("TimeLimit=0.3", {"TimeLimit": 0.3})]:
    records = repeat({**base, "params": params}, 3)
    if "objective" not in records[0]["manifest"]["result"]:
        summary(f"Gurobi, {label}", records, ["result.status"])               # no license
    elif "TimeLimit" in params:
        summary(f"Gurobi, {label}", records, ["result.status", "result.stats.work"])
    else:
        summary(f"Gurobi, {label}", records, FIELDS)

"""Lesson 10.2.2, CP-SAT: `num_search_workers` is the old name of `num_workers`, and neither name
makes parallel workers repeat; `interleave_search` does.

GridCap medium (a fictional portfolio), stopped by a deterministic limit of 2.
"""

from ortools.sat import sat_parameters_pb2
from ortools.sat.python import cp_model

from repeat import repeat, summary

fields = sat_parameters_pb2.SatParameters.DESCRIPTOR.fields_by_name
print("proto field numbers:", {name: fields[name].number for name in ("num_search_workers", "num_workers")})
solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 4
print("set num_search_workers=4 -> num_workers reads", solver.parameters.num_workers)

PLAN = ["result.objective", "result.plan_digest", "result.stats.deterministic_time"]
base = {"size": "medium", "objective": "npv", "solver": "cpsat"}
limit = {"random_seed": 7, "max_deterministic_time": 2.0}
for label, params, runs in [("num_search_workers=4", {"num_search_workers": 4}, 5),
                            ("num_search_workers=4, interleave_search", {"num_search_workers": 4, "interleave_search": True}, 3),
                            ("num_workers=4, interleave_search", {"num_workers": 4, "interleave_search": True}, 3)]:
    summary(f"CP-SAT {label}, seed 7, deterministic limit 2", repeat({**base, "params": {**params, **limit}}, runs), PLAN)

"""Lesson 4.6.3: what repeats when the same GridCap medium model is solved several times.

GridCap is a fictional utility's portfolio. Each setting is solved several times in a row. For each
quantity the program prints its value if it was the same in every run and "differs" if it was not.
The page quotes only the setting/quantity pairs that came out the same way every time we ran it.
"""

import hashlib

from ortools.sat.python import cp_model

from cpsat_plan import build, schedule
from gridcap import generate

medium = generate("medium")


def run(params: dict) -> dict:
    plan = build(medium)
    solver = cp_model.CpSolver()
    for name, value in params.items():
        setattr(solver.parameters, name, value)
    status = solver.solve(plan.model)
    starts = sorted(schedule(plan, solver).items())
    return {
        "status": solver.status_name(status),
        "objective": f"{solver.objective_value:,.0f}",
        "bound": f"{solver.best_objective_bound:,.0f}",
        "branches": f"{solver.num_branches:,}",
        "deterministic time": f"{solver.deterministic_time:.4f}",
        "plan": hashlib.sha256(repr(starts).encode()).hexdigest()[:12],   # one fingerprint per plan
        "wall time": f"{solver.wall_time:.6f}",
    }


def report(label: str, params: dict, runs: int, keys: list[str]) -> None:
    results = [run(params) for _ in range(runs)]
    print(f"{label} ({runs} runs)")
    for key in keys:
        values = {r[key] for r in results}
        print(f"  {key:<19} {values.pop() if len(values) == 1 else 'differs'}")


EVERYTHING = ["status", "objective", "bound", "branches", "deterministic time", "plan", "wall time"]
report("1 worker, seed 7, deterministic limit 3",
       {"num_workers": 1, "random_seed": 7, "max_deterministic_time": 3.0}, 3, EVERYTHING)
report("1 worker, seed 7, time limit 2 s",
       {"num_workers": 1, "random_seed": 7, "max_time_in_seconds": 2.0}, 3,
       ["branches", "deterministic time", "wall time"])
report("8 workers, seed 7, deterministic limit 3",
       {"num_workers": 8, "random_seed": 7, "max_deterministic_time": 3.0}, 4,
       ["objective", "plan", "wall time"])
report("8 workers, interleaved, seed 7, deterministic limit 3",
       {"num_workers": 8, "interleave_search": True, "random_seed": 7, "max_deterministic_time": 3.0}, 3,
       EVERYTHING)

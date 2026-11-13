"""Lesson 4.6.3: what a different random seed changes, on a model CP-SAT stops early and on one it solves.

GridCap is a fictional utility's portfolio. One worker throughout, so each line repeats for its seed.
"""

import hashlib

from ortools.sat.python import cp_model

from cpsat_plan import build, schedule
from gridcap import generate


def reproducible_solver(seed: int, work: float | None = None) -> cp_model.CpSolver:
    """A solver whose result depends only on the model, the seed and the OR-Tools version."""
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = seed
    if work is not None:
        solver.parameters.max_deterministic_time = work
    return solver


def fingerprint(plan, solver) -> str:
    return hashlib.sha256(repr(sorted(schedule(plan, solver).items())).encode()).hexdigest()[:12]


for size, work in (("medium", 3.0), ("small", None)):
    portfolio = generate(size)
    limit = f"deterministic limit {work:g}" if work else "no limit"
    print(f"{size}, {limit}")
    for seed in (1, 2, 3):
        plan = build(portfolio)
        solver = reproducible_solver(seed, work)
        status = solver.solve(plan.model)
        print(f"  seed {seed}: {solver.status_name(status):<8} plan ${solver.objective_value:,.0f}k  "
              f"branches {solver.num_branches:>6,}  plan {fingerprint(plan, solver)}")

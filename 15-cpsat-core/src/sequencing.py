"""Lesson 4.4.4: one crew, n circuits to trim in some order: big-M MILP for HiGHS against CP-SAT.

The circuits are invented for the course (a seeded random draw), in the style of GridCap, a
fictional utility. Both solvers get a deterministic work limit (HiGHS: a node limit; CP-SAT: one
worker and a deterministic-time limit), so every run repeats exactly; each is run twice to show it.
"""

import random

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from cpsat_models import solve_highs

NODE_LIMIT = 10_000       # HiGHS branch-and-bound nodes
DETERMINISTIC_TIME = 10   # CP-SAT work units (about a second each)


def circuits(n: int, seed: int = 15) -> list[tuple[int, int, int]]:
    """(days of trimming, risk weight, due day) for n circuits."""
    rng = random.Random(seed)
    jobs = [(rng.randint(2, 9), rng.randint(1, 5)) for _ in range(n)]
    total = sum(d for d, _ in jobs)
    return [(d, w, rng.randint(d, int(total * 0.6))) for d, w in jobs]


def with_highs(jobs) -> tuple[str, float, float]:
    horizon = sum(d for d, _, _ in jobs)
    model = mathopt.Model(name="sequencing")
    start = [model.add_integer_variable(lb=0, ub=horizon) for _ in jobs]
    late = [model.add_variable(lb=0, ub=horizon) for _ in jobs]
    for i, (d, _, due) in enumerate(jobs):
        model.add_linear_constraint(late[i] >= start[i] + d - due)
        for j in range(i + 1, len(jobs)):
            first = model.add_binary_variable()                # 1: circuit i is trimmed before j
            model.add_linear_constraint(start[i] + d <= start[j] + horizon * (1 - first))
            model.add_linear_constraint(start[j] + jobs[j][0] <= start[i] + horizon * first)
    model.minimize(sum(w * late[i] for i, (_, w, _) in enumerate(jobs)))
    result = solve_highs(model, mathopt.SolveParameters(node_limit=NODE_LIMIT, relative_gap_tolerance=0.0))
    return result.termination.reason.name, result.objective_value(), result.termination.objective_bounds.dual_bound


def with_cpsat(jobs) -> tuple[str, float, float]:
    horizon = sum(d for d, _, _ in jobs)
    model = cp_model.CpModel()
    start = [model.new_int_var(0, horizon, f"start_{i}") for i in range(len(jobs))]
    late = [model.new_int_var(0, horizon, f"late_{i}") for i in range(len(jobs))]
    for i, (d, _, due) in enumerate(jobs):
        model.add(late[i] >= start[i] + d - due)
        for j in range(i + 1, len(jobs)):
            first = model.new_bool_var(f"first_{i}_{j}")
            model.add(start[i] + d <= start[j]).only_enforce_if(first)
            model.add(start[j] + jobs[j][0] <= start[i]).only_enforce_if(~first)
    model.minimize(sum(w * late[i] for i, (_, w, _) in enumerate(jobs)))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.max_deterministic_time = DETERMINISTIC_TIME
    status = solver.solve(model)
    return solver.status_name(status), solver.objective_value, solver.best_objective_bound


if __name__ == "__main__":
    print(f"{'n':>3}  {'solver':6} {'status':9} {'best plan':>9} {'bound':>7}  repeats")
    for n in (8, 10, 12):
        jobs = circuits(n)
        for name, solve in (("HiGHS", with_highs), ("CP-SAT", with_cpsat)):
            first, second = solve(jobs), solve(jobs)
            status, value, bound = first
            print(f"{n:>3}  {name:6} {status:9} {value:>9,.0f} {bound:>7,.0f}  {first == second}")

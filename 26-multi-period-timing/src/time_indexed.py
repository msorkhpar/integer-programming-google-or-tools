"""Lessons 6.4.1 and 6.4.3: OR-Tools' time-indexed scheduling example, with its release times as
bounds and as variables never created, and its LP bound against a start-time model with big-M rows.

One machine runs one job at a time; job i takes p_i periods, may not start before its release time
r_i, and the goal is the smallest sum of completion times. x[i, t] = 1: job i starts at time t.
"""
# Adapted from the OR-Tools example time_indexed_scheduling.py, https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py

import itertools
import random

from ortools.math_opt.python import mathopt

from timing_model import solve_highs

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def random_jobs(num_jobs: int, seed: int) -> tuple[list[int], list[int]]:
    """Processing times from 1 to 19 and release times from 1 to 10 x num_jobs - 1, as in the example."""
    rng = random.Random(seed)
    return [rng.randrange(1, 20) for _ in range(num_jobs)], [rng.randrange(1, num_jobs * 10) for _ in range(num_jobs)]


def time_indexed(p: list[int], r: list[int], windows: str, *, integer: bool = True):
    """windows="bounds": every (i, t) created, early ones bounded to 0, as in the example;
    windows="create": no variable for a start before the release time."""
    horizon = max(r) + sum(p)
    model = mathopt.Model(name="time_indexed_scheduling")
    x = {}
    for i in range(len(p)):
        for t in range(horizon):
            if windows == "create" and t < r[i]:
                continue                                    # never created
            x[i, t] = model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{i}_{t}")
            if t < r[i]:
                x[i, t].upper_bound = 0                     # created, then forbidden
        model.add_linear_constraint(sum(v for (j, t), v in x.items() if j == i) == 1, name=f"once_{i}")
    for t in range(horizon):                                # one job running at time t
        running = [x[i, s] for i in range(len(p)) for s in range(max(0, t - p[i] + 1), t + 1) if (i, s) in x]
        if running:                                         # an empty sum has nothing to bound
            model.add_linear_constraint(sum(running) <= 1, name=f"machine_{t}")
    model.minimize(sum((t + p[i]) * v for (i, t), v in x.items()))
    return model, x


def start_time(p: list[int], r: list[int], *, integer: bool = True) -> mathopt.Model:
    """One start time per job, and for each pair 'i before j or j before i' as two big-M rows."""
    horizon = max(r) + sum(p)
    model = mathopt.Model(name="start_time_scheduling")
    s = [model.add_variable(lb=r[i], ub=horizon - p[i], name=f"s_{i}") for i in range(len(p))]
    for i, j in itertools.combinations(range(len(p)), 2):
        y = model.add_variable(lb=0, ub=1, is_integer=integer, name=f"first_{i}_{j}")
        model.add_linear_constraint(s[i] + p[i] <= s[j] + horizon * (1 - y), name=f"{i}_before_{j}")
        model.add_linear_constraint(s[j] + p[j] <= s[i] + horizon * y, name=f"{j}_before_{i}")
    model.minimize(sum(s[i] + p[i] for i in range(len(p))))
    return model


if __name__ == "__main__":
    instances = {"the example's test data": ([10, 1, 5], [0, 1, 0]), "8 random jobs, seed 3": random_jobs(8, 3)}
    print("release times as bounds or as variables never created (lesson 6.4.1):")
    for name, (p, r) in instances.items():
        for windows in ("bounds", "create"):
            model, x = time_indexed(p, r, windows)
            result = solve_highs(model, EXACT)
            starts = sorted((t, i) for (i, t), v in x.items() if result.variable_values(v) > 0.5)
            print(f"  {name:24} {windows:6} variables {model.get_num_variables():5}  "
                  f"sum of completion times {result.objective_value():.0f}  order {[i for _, i in starts]}")
    print("LP bounds, time-indexed against start times with big-M (lesson 6.4.3):")
    for name, (p, r) in instances.items():
        ti_model, _ = time_indexed(p, r, "create", integer=False)
        ti = mathopt.solve(ti_model, mathopt.SolverType.GLOP).objective_value()
        st = mathopt.solve(start_time(p, r, integer=False), mathopt.SolverType.GLOP).objective_value()
        best = solve_highs(start_time(p, r), EXACT).objective_value()
        print(f"  {name:24} time-indexed {ti:8.2f}  start-time big-M {st:8.2f}  MILP {best:.0f}")

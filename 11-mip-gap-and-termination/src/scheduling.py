"""OR-Tools' time-indexed scheduling example, solved to the end and stopped at its first plan."""
# Adapted from the OR-Tools example time_indexed_scheduling.py, https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py

import random

from ortools.math_opt.python import mathopt

from selection import solve_highs


def random_jobs(num_jobs: int, seed: int) -> tuple[list[int], list[int]]:
    """Processing times from 1 to 19 and release times from 1 to 10 x num_jobs - 1, as in the example."""
    rng = random.Random(seed)
    processing = [rng.randrange(1, 20) for _ in range(num_jobs)]
    release = [rng.randrange(1, num_jobs * 10) for _ in range(num_jobs)]
    return processing, release


def build(processing: list[int], release: list[int]) -> mathopt.Model:
    """x[i][t] = 1: job i starts at time t. One machine; minimize the sum of completion times."""
    horizon = max(release) + sum(processing)
    model = mathopt.Model(name="time_indexed_scheduling")
    x = [[model.add_binary_variable(name=f"x_{i}_{t}") for t in range(horizon)] for i in range(len(processing))]
    for i, p in enumerate(processing):
        for t in range(release[i]):
            x[i][t].upper_bound = 0                                  # not before its release time
        model.add_linear_constraint(sum(x[i]) == 1, name=f"start_{i}")
    for t in range(horizon):                                           # one job at a time
        model.add_linear_constraint(
            sum(x[i][s] for i, p in enumerate(processing) for s in range(max(0, t - p + 1), t + 1)) <= 1,
            name=f"machine_{t}")
    model.minimize(sum((t + p) * x[i][t] for i, p in enumerate(processing) for t in range(horizon)))
    return model


def report(name: str, result: mathopt.SolveResult) -> None:
    t = result.termination
    p, d = t.objective_bounds.primal_bound, t.objective_bounds.dual_bound
    hit = t.limit.name if t.limit is not None else "-"
    print(f"  {name:<16} {t.reason.name:<8} limit {hit:<8} plan {p:>5,.0f}  bound {d:>7,.1f}  "
          f"gap {p - d:>5,.0f} ({(p - d) / p:.1%})  nodes {result.solve_stats.node_count}")


if __name__ == "__main__":
    print("the example's own test instance (3 jobs):")
    report("to the end", solve_highs(build([10, 1, 5], [0, 1, 0])))
    processing, release = random_jobs(15, seed=1)
    model = build(processing, release)
    print(f"15 random jobs, {model.get_num_variables():,} binaries, minimize the sum of completion times:")
    report("to the end", solve_highs(model))
    report("first plan only", solve_highs(model, mathopt.SolveParameters(solution_limit=1, relative_gap_tolerance=0.0)))

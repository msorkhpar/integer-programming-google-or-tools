"""OR-Tools' writing-seminar assignment, solved as an LP relaxation (GLOP) and as a MILP (HiGHS)."""
# Adapted from the OR-Tools example writing_seminar.py, https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/writing_seminar.py

import random

from ortools.math_opt.python import mathopt

from selection import solve_highs

RANK_PENALTY = (0, 1, 5, 20, 100)       # penalty for giving a student their 1st, 2nd, ... 5th choice
UNMATCHED_PENALTY = 1000                # penalty for a student left without a seminar


def students(num_classes: int, seed: int) -> list[tuple[int, ...]]:
    """12 students per seminar, each ranking 5 seminars, as in the OR-Tools example."""
    rng = random.Random(seed)
    return [tuple(rng.sample(range(num_classes), len(RANK_PENALTY))) for _ in range(12 * num_classes)]


def build(ranked: list[tuple[int, ...]], num_classes: int, capacity: int, integer: bool):
    model = mathopt.Model(name="writing_seminar")
    y = [model.add_variable(lb=0, ub=1, is_integer=integer, name=f"y_{i}") for i in range(len(ranked))]
    x = [{j: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{i}_{j}") for j in r}
         for i, r in enumerate(ranked)]
    model.minimize(UNMATCHED_PENALTY * sum(y)
                   + sum(RANK_PENALTY[k] * x[i][j] for i, r in enumerate(ranked) for k, j in enumerate(r)))
    for i in range(len(ranked)):
        model.add_linear_constraint(y[i] + sum(x[i].values()) == 1, name=f"one_{i}")
    for j in range(num_classes):
        model.add_linear_constraint(sum(xi[j] for xi in x if j in xi) <= capacity, name=f"seats_{j}")
    return model


if __name__ == "__main__":
    ranked = students(num_classes=50, seed=1)
    for capacity in (15, 11):
        lp = build(ranked, 50, capacity, integer=False)
        relaxed = mathopt.solve(lp, mathopt.SolverType.GLOP)
        values = relaxed.variable_values()
        fractional = sum(1e-6 < v < 1 - 1e-6 for v in values.values())
        milp = solve_highs(build(ranked, 50, capacity, integer=True))
        print(f"{len(ranked)} students, 50 seminars of {capacity} seats, {len(values)} variables")
        print(f"  LP relaxation (GLOP): {relaxed.objective_value():,.2f}, fractional variables: {fractional}")
        print(f"  MILP (HiGHS):         {milp.objective_value():,.2f}, nodes {milp.solve_stats.node_count}")

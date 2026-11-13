"""Size is not difficulty: 400 GridCap binaries against 30 binaries in an exact-split puzzle (invented data)."""

import random

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs

NODE_LIMIT = 100_000


def exact_split(rows: int, n: int, seed: int) -> mathopt.Model:
    """Pick projects so that each of `rows` spend columns comes to exactly half its total."""
    rng = random.Random(seed)
    spend = [[rng.randint(0, 99) for _ in range(n)] for _ in range(rows)]
    model = mathopt.Model(name="exact split")
    x = [model.add_binary_variable(name=f"x_{j}") for j in range(n)]
    for r, row in enumerate(spend):
        model.add_linear_constraint(sum(a * v for a, v in zip(row, x)) == sum(row) // 2, name=f"half_{r}")
    return model


def report(label: str, n: int, result: mathopt.SolveResult) -> None:
    limit = f" (stopped: {result.termination.limit.name} limit)" if result.termination.limit else ""
    print(f"{label:<26}{n:>4} binaries  {result.termination.reason.name:<18} "
          f"{result.solve_stats.node_count:>7,} nodes{limit}")


if __name__ == "__main__":
    params = mathopt.SolveParameters(node_limit=NODE_LIMIT)
    for size in ("small", "medium"):
        portfolio = generate(size)
        report(f"GridCap {size} selection", len(portfolio.projects), solve_highs(build(portfolio).model, params))
    for rows, n in ((2, 10), (3, 20), (4, 30)):
        report(f"exact split, {rows} rows", n, solve_highs(exact_split(rows, n, seed=1), params))

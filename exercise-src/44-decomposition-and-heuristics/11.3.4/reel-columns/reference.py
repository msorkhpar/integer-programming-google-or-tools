"""Column generation for cable reels. A pricing function is given (a brute-force one, not practice 1's); write the loop."""

from __future__ import annotations

import itertools
import math

from ortools.math_opt.python import mathopt



def best_reel(prices: dict[str, float], pieces: dict[str, tuple[int, int]], reel: int) -> tuple[float, dict[str, int]]:
    """The pattern worth the most at `prices` that fits in one reel, with at most `demand` of each piece.

    Not practice 1's answer: it tries every count of every piece, which is quick for this practice's
    three lengths and too slow for practice 1's longest test.
    """
    names = list(pieces)
    best = (0.0, {})
    for counts in itertools.product(*[range(pieces[n][1] + 1) for n in names]):
        if sum(c * pieces[n][0] for n, c in zip(names, counts)) <= reel:
            worth = sum(c * prices[n] for n, c in zip(names, counts))
            if worth > best[0] + 1e-12:
                best = (worth, {n: c for n, c in zip(names, counts) if c})
    return best


def reel_columns(pieces: dict[str, tuple[int, int]], reel: int):
    """Returns (LP optimum, the lower bound after each master solve, reels in the integer plan)."""
    patterns = [{k: min(d, reel // length)} for k, (length, d) in pieces.items()]
    bounds = []
    while True:
        lp = mathopt.Model(name="reels")
        use = [lp.add_variable(lb=0, name=f"use_{i}") for i in range(len(patterns))]
        rows = {k: lp.add_linear_constraint(sum(p.get(k, 0) * u for p, u in zip(patterns, use)) >= d, name=k)
                for k, (_, d) in pieces.items()}
        lp.minimize(sum(use))
        result = mathopt.solve(lp, mathopt.SolverType.GLOP)
        worth, pattern = best_reel({k: result.dual_values(r) for k, r in rows.items()}, pieces, reel)
        bounds.append(result.objective_value() / max(worth, 1.0))
        if worth <= 1 + 1e-6:
            break
        patterns.append(pattern)
    for u in use:
        u.integer = True
    whole = mathopt.solve(lp, mathopt.SolverType.HIGHS)
    return result.objective_value(), bounds, round(whole.objective_value())


if __name__ == "__main__":
    print(reel_columns({"feeder": (70, 9), "service": (50, 14), "lateral": (30, 11)}, 220))

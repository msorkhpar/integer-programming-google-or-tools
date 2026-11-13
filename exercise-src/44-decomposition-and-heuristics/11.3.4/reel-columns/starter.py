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
    # TODO: write the restricted master and the stopping rule first, then the loop.
    return 0.0, [], 0


if __name__ == "__main__":
    print(reel_columns({"feeder": (70, 9), "service": (50, 14), "lateral": (30, 11)}, 220))

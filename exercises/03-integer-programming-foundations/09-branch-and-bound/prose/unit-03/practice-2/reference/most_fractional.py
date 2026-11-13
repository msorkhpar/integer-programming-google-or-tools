from __future__ import annotations

import math


def most_fractional(x: dict[str, float], tol: float = 1e-6) -> str | None:
    """The candidate farthest from a whole number; the first listed among ties; None if none."""
    best, best_score = None, 0.0
    for name, v in x.items():
        score = min(v - math.floor(v), math.ceil(v) - v)
        if score > tol and score > best_score:
            best, best_score = name, score
    return best


if __name__ == "__main__":
    print(most_fractional({"crews_east": 2.0, "crews_west": 1.35, "open_depot": 0.8}))

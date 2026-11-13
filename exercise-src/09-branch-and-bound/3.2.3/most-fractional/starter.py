from __future__ import annotations

import math


def most_fractional(x: dict[str, float], tol: float = 1e-6) -> str | None:
    """The candidate farthest from a whole number; the first listed among ties; None if none."""
    # TODO: score each value by its distance to the nearer whole number; keep the largest score
    # above tol, the first one listed among ties.
    return next(iter(x), "")


if __name__ == "__main__":
    print(most_fractional({"crews_east": 2.0, "crews_west": 1.35, "open_depot": 0.8}))

from __future__ import annotations

from typing import Callable

Point = tuple[float, float]


def supported_points(best_for: Callable[[float], Point]) -> list[Point]:
    """Every point a weighted sum can return, found by asking `best_for` for chosen shares.

    `best_for(s)` solves max s*first + (1-s)*second and returns the (first, second) values of a best
    option. The result is sorted by the first value.
    """
    def score(p: Point, s: float) -> float:
        return s * p[0] + (1 - s) * p[1]

    def between(a: Point, b: Point) -> list[Point]:
        s = (a[1] - b[1]) / ((b[0] - a[0]) + (a[1] - b[1]))     # the share at which a and b tie
        c = best_for(s)
        if score(c, s) <= score(a, s) + 1e-9:                  # nothing above the segment a-b
            return []
        return between(a, c) + [c] + between(c, b)

    left, right = best_for(0.0), best_for(1.0)
    if left == right:
        return [left]
    return [left] + between(left, right) + [right]


if __name__ == "__main__":
    front = [(0, 10), (6, 7), (10, 0)]
    print(supported_points(lambda s: max(front, key=lambda p: (s * p[0] + (1 - s) * p[1], p[0], p[1]))))

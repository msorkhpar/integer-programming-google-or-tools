from __future__ import annotations

from typing import Callable

Point = tuple[float, float]


def supported_points(best_for: Callable[[float], Point]) -> list[Point]:
    """Every point a weighted sum can return, found by asking `best_for` for chosen shares.

    `best_for(s)` solves max s*first + (1-s)*second and returns the (first, second) values of a best
    option. The result is sorted by the first value.
    """
    # TODO: start from the two ends and ask for the points between them.
    return [best_for(0.0), best_for(1.0)]


if __name__ == "__main__":
    front = [(0, 10), (6, 7), (10, 0)]
    print(supported_points(lambda s: max(front, key=lambda p: (s * p[0] + (1 - s) * p[1], p[0], p[1]))))

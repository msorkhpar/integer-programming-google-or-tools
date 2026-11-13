from __future__ import annotations

from itertools import combinations

TOL = 1e-9


def vertices(rows: list[tuple[float, float, float]]) -> list[tuple[float, float]]:
    """Every corner of the region {(x, y): a*x + b*y <= r for each row (a, b, r)}, sorted, each once."""
    # TODO: cross every pair of rows' lines with Cramer's rule (skip parallel pairs), keep a crossing
    # only if every row allows it (within TOL), round to 6 decimals, list each corner once, sorted.
    return []


if __name__ == "__main__":
    square = [(-1, 0, 0), (0, -1, 0), (1, 0, 2), (0, 1, 2)]
    print(vertices(square))

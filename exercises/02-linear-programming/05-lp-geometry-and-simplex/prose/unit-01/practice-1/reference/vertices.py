from __future__ import annotations

from itertools import combinations

TOL = 1e-9


def vertices(rows: list[tuple[float, float, float]]) -> list[tuple[float, float]]:
    """Every corner of the region {(x, y): a*x + b*y <= r for each row (a, b, r)}, sorted, each once."""
    found = set()
    for (a1, b1, r1), (a2, b2, r2) in combinations(rows, 2):
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-12:
            continue
        x = (r1 * b2 - r2 * b1) / det
        y = (a1 * r2 - a2 * r1) / det
        if all(a * x + b * y <= r + TOL for a, b, r in rows):
            found.add((round(x, 6) + 0.0, round(y, 6) + 0.0))
    return sorted(found)


if __name__ == "__main__":
    square = [(-1, 0, 0), (0, -1, 0), (1, 0, 2), (0, 1, 2)]
    print(vertices(square))

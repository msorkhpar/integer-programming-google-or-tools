"""A vertex of a 2-variable region is where two boundary lines cross, at a point every row allows."""

from itertools import combinations

from half_planes import ALL, broken


def crossing(row1, row2):
    """Where the lines a.x = b of two rows meet (Cramer's rule), or None when they are parallel."""
    (a1, b1), r1 = row1
    (a2, b2), r2 = row2
    det = a1 * b2 - a2 * b1
    if abs(det) < 1e-12:
        return None
    return ((r1 * b2 - r2 * b1) / det, (a1 * r2 - a2 * r1) / det)


def vertices(rows=ALL) -> dict[tuple[float, float], list[str]]:
    """Every feasible crossing point, with the rows tight there."""
    found = {}
    for (l1, row1), (l2, row2) in combinations(rows.items(), 2):
        point = crossing(row1, row2)
        if point is not None and not broken(*point, rows):
            point = (round(point[0], 9) + 0.0, round(point[1], 9) + 0.0)
            found.setdefault(point, [])
            found[point] += [label for label in (l1, l2) if label not in found[point]]
    return found


if __name__ == "__main__":
    for (l1, row1), (l2, row2) in combinations(ALL.items(), 2):
        point = crossing(row1, row2)
        if point is None:
            verdict = "parallel, never meet"
        else:
            rows = broken(*point)
            verdict = f"({point[0] + 0.0:g}, {point[1] + 0.0:g}) " + ("VERTEX" if not rows else "outside: breaks " + ", ".join(rows))
        print(f"{l1:>8} x {l2:<8} {verdict}")
    print(len(vertices()), "vertices:", ", ".join(f"({d:g}, {t:g})" for d, t in vertices()))

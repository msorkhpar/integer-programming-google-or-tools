"""Every pair of rows made tight at once: a parallel pair, a point outside, or an extreme point."""

import itertools

import numpy as np

from polygon import A, b, c, is_feasible, names


def corners() -> list[tuple[str, str, np.ndarray | None, str]]:
    found = []
    for i, k in itertools.combinations(range(len(b)), 2):
        pair = A[[i, k]]
        if abs(np.linalg.det(pair)) < 1e-12:
            found.append((names[i], names[k], None, "parallel"))
            continue
        point = np.linalg.solve(pair, b[[i, k]]) + 0.0   # both rows hold with equality; + 0.0 turns -0 into 0
        found.append((names[i], names[k], point, "vertex" if is_feasible(point) else "outside"))
    return found


if __name__ == "__main__":
    vertices = []
    for row_i, row_k, point, kind in corners():
        where = "" if point is None else f"(d, v) = ({point[0]:.0f}, {point[1]:.0f})"
        value = f"objective {c @ point:,.0f}" if kind == "vertex" else ""
        print(f"{row_i:>10} & {row_k:<10} {kind:8} {where:24} {value}")
        if kind == "vertex":
            vertices.append(point)
    best = max(vertices, key=lambda p: c @ p)
    print(f"{len(vertices)} vertices; best (d, v) = ({best[0]:.0f}, {best[1]:.0f}), objective {c @ best:,.0f}")

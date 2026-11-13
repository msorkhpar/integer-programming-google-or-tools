from __future__ import annotations

import itertools

import numpy as np


def best_corner(A: np.ndarray, b: np.ndarray, c: np.ndarray, tol: float = 1e-9) -> tuple[float, tuple[float, float]] | None:
    """The vertex of {x : A @ x <= b} in two variables that maximizes c @ x, as (value, (x0, x1))."""
    A, b, c = np.asarray(A, dtype=float), np.asarray(b, dtype=float), np.asarray(c, dtype=float)
    best = None
    for i, k in itertools.combinations(range(len(b)), 2):
        pair = A[[i, k]]
        if abs(np.linalg.det(pair)) < 1e-12:
            continue
        point = np.linalg.solve(pair, b[[i, k]])
        if np.any(A @ point > b + tol):
            continue
        value = float(c @ point)
        if best is None or value > best[0]:
            best = (value, (float(point[0]), float(point[1])))
    return best


if __name__ == "__main__":
    A = np.array([[1, 1], [-1, 0], [0, -1]])
    print(best_corner(A, np.array([4, 0, 0]), np.array([1, 2])))

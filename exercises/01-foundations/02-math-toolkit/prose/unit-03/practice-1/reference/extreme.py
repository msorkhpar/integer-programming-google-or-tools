from __future__ import annotations

import numpy as np


def is_extreme_point(A: np.ndarray, b: np.ndarray, x: np.ndarray, tol: float = 1e-9) -> bool:
    """True when x is a vertex of the polyhedron {x : A @ x <= b}."""
    A, b, x = np.asarray(A, dtype=float), np.asarray(b, dtype=float), np.asarray(x, dtype=float)
    activity = A @ x
    if np.any(activity > b + tol):
        return False
    tight = A[np.abs(activity - b) <= tol]
    return bool(len(tight) > 0 and np.linalg.matrix_rank(tight) == A.shape[1])


if __name__ == "__main__":
    square = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])
    print(is_extreme_point(square, np.array([1, 1, 0, 0]), np.array([1, 0])))

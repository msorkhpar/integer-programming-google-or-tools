from __future__ import annotations

import numpy as np


def is_extreme_point(A: np.ndarray, b: np.ndarray, x: np.ndarray, tol: float = 1e-9) -> bool:
    """True when x is a vertex of the polyhedron {x : A @ x <= b}."""
    # TODO: feasible first; then find the tight rows and count how many are independent.
    return None


if __name__ == "__main__":
    square = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])
    print(is_extreme_point(square, np.array([1, 1, 0, 0]), np.array([1, 0])))

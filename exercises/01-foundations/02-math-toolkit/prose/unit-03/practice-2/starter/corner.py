from __future__ import annotations

import itertools

import numpy as np


def best_corner(A: np.ndarray, b: np.ndarray, c: np.ndarray, tol: float = 1e-9) -> tuple[float, tuple[float, float]] | None:
    """The vertex of {x : A @ x <= b} in two variables that maximizes c @ x, as (value, (x0, x1))."""
    # TODO: solve every pair of rows, keep the feasible crossings, and return the best one.
    return 0.0, (0.0, 0.0)


if __name__ == "__main__":
    A = np.array([[1, 1], [-1, 0], [0, -1]])
    print(best_corner(A, np.array([4, 0, 0]), np.array([1, 2])))

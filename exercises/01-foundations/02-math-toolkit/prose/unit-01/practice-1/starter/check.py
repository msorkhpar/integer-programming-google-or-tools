from __future__ import annotations

import numpy as np


def broken_rows(A: np.ndarray, b: np.ndarray, x: np.ndarray, tol: float = 1e-9) -> list[int]:
    """The indices of the rows of A @ x <= b that x breaks by more than tol, in increasing order."""
    # TODO: compute every row's activity at once and list the rows over their limit.
    return [-1]


def is_feasible(A: np.ndarray, b: np.ndarray, x: np.ndarray, tol: float = 1e-9) -> bool:
    """True when x satisfies every row of A @ x <= b, each within tol."""
    # TODO: one line of NumPy.
    return False


if __name__ == "__main__":
    A = np.array([[3, 2, 0], [0, 1, 1]])
    b = np.array([5, 1])
    x = np.array([1, 1, 1])
    print(is_feasible(A, b, x), broken_rows(A, b, x))

"""Floating-point sums can miss an exact bound by a hair, so a feasibility check needs a tolerance."""

import numpy as np

A = np.array([[0.1, 0.1, 0.1]])
b = np.array([0.3])
x = np.array([1.0, 1.0, 1.0])


def is_feasible(A: np.ndarray, b: np.ndarray, x: np.ndarray, tol: float = 1e-9) -> bool:
    return bool(np.all(A @ x <= b + tol))


if __name__ == "__main__":
    print("A @ x       =", float((A @ x)[0]))
    print("A @ x <= b  =", bool(np.all(A @ x <= b)))
    print("with tol    =", is_feasible(A, b, x))

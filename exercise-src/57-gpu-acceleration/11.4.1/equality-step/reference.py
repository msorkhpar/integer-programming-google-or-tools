from __future__ import annotations

import numpy as np


def pdhg_step(A, b, c, u, x, y, tau: float, sigma: float):
    """One PDHG iteration for  min c'x  s.t.  A x = b,  0 <= x <= u.  Returns (x_new, y_new)."""
    x_new = np.clip(x - tau * (c - A.T @ y), 0.0, u)
    y_new = y + sigma * (b - A @ (2 * x_new - x))
    return x_new, y_new


def solve(A, b, c, u, iterations: int):
    """Run pdhg_step from zero with tau = sigma = 0.9 / ||A||_F; return the last x and y."""
    tau = sigma = 0.9 / np.linalg.norm(A)
    x, y = np.zeros(A.shape[1]), np.zeros(A.shape[0])
    for _ in range(iterations):
        x, y = pdhg_step(A, b, c, u, x, y, tau, sigma)
    return x, y


if __name__ == "__main__":
    A = np.array([[1.0, 1.0]])
    x, y = solve(A, np.array([4.0]), np.array([1.0, 2.0]), np.array([3.0, 3.0]), 2000)
    print(np.round(x, 4), np.round(y, 4))

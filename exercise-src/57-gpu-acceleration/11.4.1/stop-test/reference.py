from __future__ import annotations

import numpy as np


def converged(A, b, c, x, y, eps: float) -> bool:
    """PDLP's three relative tests for  min c'x  s.t.  A x >= b,  x >= 0, with prices y >= 0."""
    primal_obj, dual_obj = float(c @ x), float(b @ y)
    gap_ok = abs(primal_obj - dual_obj) <= eps * (1 + abs(primal_obj) + abs(dual_obj))
    shortfall = np.maximum(0.0, b - A @ x)                  # only rows the plan leaves short
    primal_ok = np.linalg.norm(shortfall) <= eps * (1 + np.linalg.norm(b))
    wrong_sign = np.maximum(0.0, -(c - A.T @ y))            # x >= 0 needs every reduced cost >= 0
    dual_ok = np.linalg.norm(wrong_sign) <= eps * (1 + np.linalg.norm(c))
    return bool(gap_ok and primal_ok and dual_ok)


if __name__ == "__main__":
    A = np.array([[1.0, 1.0], [1.0, 2.0]])
    print(converged(A, np.array([4.0, 6.0]), np.array([2.0, 3.0]), np.array([2.0, 2.0]), np.array([1.0, 1.0]), 1e-6))

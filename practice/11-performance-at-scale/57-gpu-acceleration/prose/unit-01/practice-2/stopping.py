from __future__ import annotations

import numpy as np


def converged(A, b, c, x, y, eps: float) -> bool:
    """PDLP's three relative tests for  min c'x  s.t.  A x >= b,  x >= 0, with prices y >= 0."""
    # TODO: the gap, the primal residual and the dual residual, each against its relative limit.
    return False

if __name__ == "__main__":
    A = np.array([[1.0, 1.0], [1.0, 2.0]])
    print(converged(A, np.array([4.0, 6.0]), np.array([2.0, 3.0]), np.array([2.0, 2.0]), np.array([1.0, 1.0]), 1e-6))

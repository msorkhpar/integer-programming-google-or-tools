from __future__ import annotations

from fractions import Fraction
from math import floor


def gomory_in_x(row: list[Fraction], A: list[list[int]], b: list[int]) -> tuple[list[Fraction], Fraction]:
    """The Gomory cut of a tableau row, as  sum_j g_j x_j <= h  in the original variables."""
    n, m = len(A[0]), len(A)
    f = [v - floor(v) for v in row]
    g = [-f[j] + sum(f[n + i] * A[i][j] for i in range(m)) for j in range(n)]
    h = sum(f[n + i] * b[i] for i in range(m)) - f[-1]
    return g, h


if __name__ == "__main__":
    F = Fraction
    print(gomory_in_x([F(1), F(0), F(1, 4), F(1, 2), F(9, 4)], [[2, 1], [1, 3]], [7, 9]))

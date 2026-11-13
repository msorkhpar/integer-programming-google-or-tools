from __future__ import annotations

from fractions import Fraction
from math import floor


def gomory_in_x(row: list[Fraction], A: list[list[int]], b: list[int]) -> tuple[list[Fraction], Fraction]:
    """The Gomory cut of a tableau row, as  sum_j g_j x_j <= h  in the original variables."""
    n, m = len(A[0]), len(A)
    # TODO: take the fractional part v - floor(v) of every entry and of the right-hand side, then
    # substitute s_i = b_i - A_i x into  sum_k f(r_k) w_k >= f(r_0).
    return [Fraction(0)] * n, Fraction(0)


if __name__ == "__main__":
    F = Fraction
    print(gomory_in_x([F(1), F(0), F(1, 4), F(1, 2), F(9, 4)], [[2, 1], [1, 3]], [7, 9]))

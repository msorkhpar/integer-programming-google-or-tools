"""An exact tableau simplex (fractions, not floats) and the Gomory fractional cut read off its rows.

The LP is  max c.x  s.t.  A x <= b, x >= 0, with integer A and b and every b_i >= 0, so the slack
basis at x = 0 is a vertex to start from (lesson 2.2.2 builds the same tableau with floats).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import floor


@dataclass
class Tableau:
    rows: list[list[Fraction]]        # constraint rows, then the objective row; each ends with its rhs
    basis: list[int]                  # basis[i] = the column basic in row i
    names: list[str]


def build(A, b, c, names: list[str]) -> Tableau:
    m, n = len(A), len(c)
    rows = [[Fraction(v) for v in A[i]] + [Fraction(int(i == j)) for j in range(m)] + [Fraction(b[i])]
            for i in range(m)]
    rows.append([Fraction(-v) for v in c] + [Fraction(0)] * m + [Fraction(0)])
    return Tableau(rows, list(range(n, n + m)), list(names) + [f"s{i + 1}" for i in range(m)])


def pivot(T: Tableau, r: int, k: int) -> None:
    row = [v / T.rows[r][k] for v in T.rows[r]]
    T.rows = [row if i == r else [v - T.rows[i][k] * w for v, w in zip(T.rows[i], row)]
              for i in range(len(T.rows))]
    T.basis[r] = k


def solve(T: Tableau) -> Tableau:
    """Dantzig's rule and the ratio test until no objective-row entry is negative."""
    while True:
        z = T.rows[-1][:-1]
        k = min(range(len(z)), key=lambda j: (z[j], j))
        if z[k] >= 0:
            return T
        ratios = [(T.rows[i][-1] / T.rows[i][k], i) for i in range(len(T.rows) - 1) if T.rows[i][k] > 0]
        pivot(T, min(ratios)[1], k)


def value_of(T: Tableau, column: int) -> Fraction:
    return T.rows[T.basis.index(column)][-1] if column in T.basis else Fraction(0)


def frac(v: Fraction) -> Fraction:
    """The fractional part v - floor(v): always in [0, 1), also for negative v (frac(-1/4) = 3/4)."""
    return v - floor(v)


def gomory(row: list[Fraction]) -> tuple[list[Fraction], Fraction]:
    """The Gomory cut of one tableau row:  sum_j frac(a_j) w_j >= frac(b), over every column j.

    Basic columns have entries 0 or 1 in the row, so only nonbasic columns get a nonzero coefficient.
    """
    return [frac(v) for v in row[:-1]], frac(row[-1])


def in_original_variables(coef: list[Fraction], rhs: Fraction, A, b) -> tuple[list[Fraction], Fraction]:
    """Substitute s_i = b_i - A_i x into  coef . (x, s) >= rhs  and return it as  g . x <= h."""
    n, m = len(A[0]), len(A)
    g = [-coef[j] + sum(coef[n + i] * A[i][j] for i in range(m)) for j in range(n)]
    h = sum(coef[n + i] * b[i] for i in range(m)) - rhs
    return g, h


def show(T: Tableau) -> list[str]:
    width = 8
    head = "basis".rjust(width) + "".join(nm.rjust(width) for nm in T.names) + "rhs".rjust(width)
    lines = [head]
    for i, row in enumerate(T.rows):
        label = T.names[T.basis[i]] if i < len(T.basis) else "obj"
        lines.append(label.rjust(width) + "".join(str(v).rjust(width) for v in row))
    return lines

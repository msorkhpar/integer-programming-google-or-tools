"""A tiny tableau simplex for  max c.x  s.t.  A x <= b, x >= 0, with every b_i >= 0.

The tableau has one row per constraint, [A | I | b], and a last row for the objective,
[-c | 0 | z]. The slack columns start as the basis, so the first vertex is x = 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

EPS = 1e-9


def tableau(A: list[list[float]], b: list[float], c: list[float]) -> list[list[float]]:
    m = len(A)
    rows = [list(map(float, A[i])) + [1.0 if j == i else 0.0 for j in range(m)] + [float(b[i])]
            for i in range(m)]
    return rows + [[-float(cj) for cj in c] + [0.0] * m + [0.0]]


def pivot(T: list[list[float]], r: int, k: int) -> list[list[float]]:
    """Make column k a unit column with its 1 in row r: one step to a neighbouring vertex."""
    row = [v / T[r][k] for v in T[r]]
    return [row if i == r else [v - T[i][k] * w for v, w in zip(T[i], row)] for i in range(len(T))]


def entering(T: list[list[float]]) -> int | None:
    """The column with the most negative entry in the objective row; None when none improves."""
    z = T[-1][:-1]
    k = min(range(len(z)), key=lambda j: z[j])
    return k if z[k] < -EPS else None


def leaving(T: list[list[float]], k: int) -> int | None:
    """The ratio test: the row whose b_i / a_ik is smallest over a_ik > 0; None when no row limits k."""
    ratios = [(T[i][-1] / T[i][k], i) for i in range(len(T) - 1) if T[i][k] > EPS]
    return min(ratios)[1] if ratios else None


@dataclass
class Result:
    status: str
    x: list[float]
    value: float
    steps: list[tuple[str, str, float, list[float], float]] = field(default_factory=list)
    direction: list[float] | None = None


def solve(A, b, c, names: list[str], max_steps: int = 50) -> Result:
    n, m = len(c), len(A)
    T, basis, steps = tableau(A, b, c), list(range(n, n + m)), []

    def point(T):
        x = [0.0] * (n + m)
        for i, j in enumerate(basis):
            x[j] = T[i][-1]
        return x

    for _ in range(max_steps):
        k = entering(T)
        if k is None:
            return Result("OPTIMAL", point(T)[:n], T[-1][-1], steps)
        r = leaving(T, k)
        if r is None:
            direction = [0.0] * (n + m)
            direction[k] = 1.0
            for i, j in enumerate(basis):
                direction[j] = -T[i][k]
            return Result("UNBOUNDED", point(T)[:n], T[-1][-1], steps, direction[:n])
        step = T[r][-1] / T[r][k]
        T, left = pivot(T, r, k), names[basis[r]]
        basis[r] = k
        steps.append((names[k], left, step, point(T)[:n], T[-1][-1]))
    return Result("STEP_LIMIT", point(T)[:n], T[-1][-1], steps)


def fmt(v: float) -> str:
    """A tableau entry as a short fraction, so 0.6666... reads 2/3."""
    return str(Fraction(v).limit_denominator(1000))


def show(T: list[list[float]], names: list[str], basis: list[int]) -> None:
    print(f"{'basis':>9}" + "".join(f"{name:>10}" for name in names) + f"{'rhs':>10}")
    for i, row in enumerate(T):
        label = names[basis[i]] if i < len(basis) else "objective"
        print(f"{label:>9}" + "".join(f"{fmt(v):>10}" for v in row))

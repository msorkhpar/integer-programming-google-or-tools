"""Lesson 2.4.1: the bare primal-dual hybrid gradient step that PDLP is built on, by hand on a tiny LP.

max 3 x1 + 2 x2  s.t.  x1 + x2 <= 4,  x1 + 3 x2 <= 7,  x1 <= 3,  x1, x2 >= 0   (optimum 11 at (3, 1)).
PDLP adds rescaling, presolve, adaptive step sizes and restarts to this step; none of them is here.
"""

A = [[1, 1], [1, 3], [1, 0]]
b = [4, 7, 3]
c = [3, 2]
TAU = SIGMA = 0.25           # step sizes; TAU * SIGMA * ||A||^2 < 1 keeps the method converging
TOL = 1e-6


def times(M, v):             # M v
    return [sum(m * x for m, x in zip(row, v)) for row in M]


def times_t(M, v):           # M^T v
    return [sum(M[i][j] * v[i] for i in range(len(M))) for j in range(len(M[0]))]


def pdhg(report=print) -> tuple[list[float], list[float], int]:
    """Run the bare PDHG step until all three measures are within TOL; return x, y and the iteration."""
    x, y = [0.0, 0.0], [0.0, 0.0, 0.0]
    report(f"{'iter':>5} {'x1':>8} {'x2':>8} {'y1':>8} {'y2':>8} {'y3':>8} {'broken rows':>12} {'uncovered':>10} {'gap':>10}")
    for k in range(100_000):
        Ax, ATy = times(A, x), times_t(A, y)
        broken = max(max(0.0, ai - bi) for ai, bi in zip(Ax, b))           # how far x breaks a row
        uncovered = max(max(0.0, cj - aj) for cj, aj in zip(c, ATy))        # how far prices fail to cover c
        gap = abs(sum(bi * yi for bi, yi in zip(b, y)) - sum(cj * xj for cj, xj in zip(c, x)))
        done = max(broken, uncovered, gap) <= TOL
        if k in (0, 1, 2, 5, 10, 20, 50, 100, 200) or done:
            report(f"{k:5} {x[0]:8.4f} {x[1]:8.4f} {y[0]:8.4f} {y[1]:8.4f} {y[2]:8.4f} "
                   f"{broken:12.2e} {uncovered:10.2e} {gap:10.2e}")
        if done:
            return x, y, k
        # Primal step: move x up the gradient of the Lagrangian in x, c - A^T y (each activity's
        # reduced cost), then clip to x >= 0.
        x_new = [max(0.0, xj + TAU * (cj - aj)) for xj, cj, aj in zip(x, c, ATy)]
        # Dual step: move y down the gradient in y, b - A x, at the extrapolated point 2 x_new - x;
        # a broken row (A x > b) raises its price, a row with room lowers it; then clip to y >= 0.
        Ax_bar = times(A, [2 * n - o for n, o in zip(x_new, x)])
        y = [max(0.0, yi - SIGMA * (bi - ai)) for yi, bi, ai in zip(y, b, Ax_bar)]
        x = x_new
    raise RuntimeError("no convergence")


if __name__ == "__main__":
    pdhg()

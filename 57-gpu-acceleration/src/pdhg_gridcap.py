"""Plain PDHG, vectorised, on GridCap small's LP relaxation: each iteration is one product with A, one with
A transposed, and two clips. Constant steps and no restarts: what PDLP starts from. Run once on the model as
it is, and once after rescaling its rows and columns (PDLP's diagonal preconditioning).

    max c'x   s.t.  l_c <= A x <= u_c,   l <= x <= u

with one price y_r per row: y_r > 0 prices the row's upper side, y_r < 0 its lower side. GridCap is fictional.
"""

import numpy as np
import scipy.sparse

from lps import gridcap_timing, highs, relative_difference, violation

m, keys = gridcap_timing("small")
A0 = scipy.sparse.csr_matrix((m["values"], m["indices"], m["offsets"]), shape=(len(m["row_lb"]), len(m["c"])))


def pdhg(A, c, lo, hi, row_lo, row_hi, iterations: int):
    """Yield (k, x) after each iteration of plain PDHG with equal constant steps."""
    tau = sigma = 0.9 / scipy.sparse.linalg.norm(A, "fro")     # ||A||_F >= ||A||_2, so tau sigma ||A||^2 < 1
    x, y = np.zeros(A.shape[1]), np.zeros(A.shape[0])
    for k in range(1, iterations + 1):
        x_new = np.clip(x + tau * (c - A.T @ y), lo, hi)                          # primal: up the gradient, clip
        v = y + sigma * (A @ (2 * x_new - x))                                      # dual: at the look-ahead point
        y = np.maximum(0.0, v - sigma * row_hi) + np.minimum(0.0, v - sigma * row_lo)   # clip by the row's sides
        x = x_new
        yield k, x


def ruiz(A, rounds: int = 10):
    """Row and column scalings r, s that bring every row's and column's largest |entry| near 1."""
    r, s = np.ones(A.shape[0]), np.ones(A.shape[1])
    for _ in range(rounds):
        B = scipy.sparse.diags(r) @ A @ scipy.sparse.diags(s)
        r /= np.sqrt(abs(B).max(axis=1).toarray().ravel())
        s /= np.sqrt(abs(B).max(axis=0).toarray().ravel())
    return r, s


exact = highs(m, "simplex")["objective"]
c, lo, hi = np.array(m["c"]), np.array(m["lb"]), np.array(m["ub"])
row_lo, row_hi = np.array(m["row_lb"]), np.array(m["row_ub"])
print(f"A: {A0.shape[0]} x {A0.shape[1]}, {A0.nnz} nonzeros, entries from {abs(A0).data.min():g} to "
      f"{abs(A0).data.max():g}; simplex optimum {exact:,.4f}")
print(f"work per iteration: 2 x {A0.nnz} multiply-adds for A x and A'y, plus {A0.shape[0] + A0.shape[1]} clips; "
      f"no factorization")

r, s = ruiz(A0)
A1 = scipy.sparse.diags(r) @ A0 @ scipy.sparse.diags(s)        # solve for x' = x / s, then x = s * x'
print(f"rescaled: entries from {abs(A1).data.min():.2f} to {abs(A1).data.max():.2f}")
runs = {"as built": (A0, c, lo, hi, row_lo, row_hi, np.ones(len(c))),
        "rescaled": (A1, c * s, lo / s, hi / s, row_lo * r, row_hi * r, s)}
for label, (A, cc, l, u, rl, ru, back) in runs.items():
    print(f"{label}: tau = sigma = {0.9 / scipy.sparse.linalg.norm(A, 'fro'):.2e}")
    print("  iteration     objective   rel. error  max violation")
    for k, xs in pdhg(A, cc, l, u, rl, ru, 100_000):
        if k in (10, 100, 1_000, 10_000, 100_000):
            x = xs * back
            z = float(c @ x)
            print(f"  {k:9,d}  {z:12,.4f}  {relative_difference(z, exact):10.1e}  {violation(m, list(x)):13.1e}")

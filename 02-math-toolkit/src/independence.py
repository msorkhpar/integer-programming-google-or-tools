"""Linear combinations, linear independence and rank; a 2x2 determinant; the tight rows at a point.

The split of polygon.py has n = 2 variables (d and v), so its points live in two dimensions.
"""

import numpy as np

from polygon import A, b, names

rows = np.array([[1, 0],
                 [0, 1],
                 [1, 1]])

if __name__ == "__main__":
    combo = 1 * rows[0] + 1 * rows[1]            # a linear combination of rows 0 and 1
    print("1*(1, 0) + 1*(0, 1) =", tuple(combo.tolist()), " equals row 2:", bool(np.all(combo == rows[2])))
    print("rank of (1, 0), (0, 1), (1, 1):", np.linalg.matrix_rank(rows))
    print("rank of (1, 0), (0, 1):        ", np.linalg.matrix_rank(rows[:2]))
    print("rank of (1, 1), (2, 2):        ", np.linalg.matrix_rank(np.array([[1, 1], [2, 2]])))

    print()
    for i, k in ((0, 1), (2, 4)):
        (p, q), (r, s) = A[[i, k]]
        print(f"det {names[i]} & {names[k]}: {p}*{s} - {q}*{r} = {p * s - q * r},"
              f" np.linalg.det gives {np.linalg.det(A[[i, k]]):.1f}")

    print()
    for point in (np.array([2000, 1000]), np.array([1000, 500])):
        tight = np.abs(A @ point - b) <= 1e-9        # a boolean mask, one entry per row
        T = A[tight]                                 # only the rows where the mask is True
        print(f"(d, v) = {tuple(point.tolist())}: tight {[n for n, t in zip(names, tight) if t]},"
              f" A[tight] has shape {T.shape}, rank {np.linalg.matrix_rank(T)}")

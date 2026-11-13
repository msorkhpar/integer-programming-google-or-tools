"""A @ x on the CSR matrix equals A @ x on the dense one, for the medium and the large portfolio."""

import numpy as np

from gridcap import generate
from model_matrix import csr, stored_bytes

if __name__ == "__main__":
    for size in ("medium", "large"):
        A, b, names = csr(generate(size))
        dense = A.toarray()
        x = np.zeros(A.shape[1], dtype=int)
        x[::3] = 1                                     # fund every third project
        same = np.array_equal(A @ x, dense @ x)
        broken = int(np.sum(A @ x > b))
        print(f"{size:6} same activities: {same}, rows broken: {broken} of {A.shape[0]},"
              f" dense {dense.nbytes / 1e6:.1f} MB, CSR {stored_bytes(A) / 1e6:.2f} MB")
        if size == "large":
            print(f"       {A.nnz:,} nonzeros and {len(A.indptr):,} indptr entries: CSR {stored_bytes(A):,} bytes,"
                  f" dense {dense.nbytes:,} bytes")

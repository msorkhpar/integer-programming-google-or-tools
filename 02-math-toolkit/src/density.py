"""How many entries of GridCap's model matrix are nonzero, from tiny to large."""

from gridcap import generate
from model_matrix import csr, stored_bytes

if __name__ == "__main__":
    print(f"{'size':6} {'rows':>5} {'cols':>6} {'entries':>10} {'nonzeros':>8} {'density':>8}"
          f" {'dense MB':>9} {'CSR MB':>7}")
    for size in ("tiny", "small", "medium", "large"):
        A, b, names = csr(generate(size))
        rows, cols = A.shape
        print(f"{size:6} {rows:>5} {cols:>6} {rows * cols:>10,} {A.nnz:>8,} {A.nnz / (rows * cols):>8.2%}"
              f" {rows * cols * 8 / 1e6:>9.3f} {stored_bytes(A) / 1e6:>7.3f}")

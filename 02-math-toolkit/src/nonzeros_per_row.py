"""Why the matrix is sparse: each kind of row touches only a few projects."""

from collections import defaultdict

from gridcap import generate
from model_matrix import csr

if __name__ == "__main__":
    A, b, names = csr(generate("large"))
    per_kind = defaultdict(list)
    for i, name in enumerate(names):
        per_kind[name.split("_")[0]].append(A.indptr[i + 1] - A.indptr[i])
    print(f"large: {A.shape[1]:,} columns")
    for kind, counts in per_kind.items():
        print(f"{kind:7} rows: {len(counts):>4}, nonzeros per row: {min(counts):>5} to {max(counts):>5},"
              f" mean {sum(counts) / len(counts):>7.1f}")

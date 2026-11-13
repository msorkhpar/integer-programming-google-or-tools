"""The tiny model matrix as triplets, then as CSR's three arrays, and one row read back."""

from scipy import sparse

from gridcap import generate
from model_matrix import triplets

tiny = generate("tiny")
rows, cols, vals, names, rhs = triplets(tiny)

if __name__ == "__main__":
    print("first rows as triplets (row, col, value):")
    for r, c, v in list(zip(rows, cols, vals))[:9]:
        print(f"  ({r}, {c}, {v})  {names[r]} x {tiny.project_ids[c]}")
    print(f"{len(names)} rows, {len(vals)} nonzeros")

    A = sparse.coo_array((vals, (rows, cols)), shape=(len(names), len(tiny.projects))).tocsr()
    print("indptr :", A.indptr.tolist())
    print("indices:", A.indices.tolist())
    print("data   :", A.data.tolist())
    print("bytes per entry: data", A.data.itemsize, " indices", A.indices.itemsize, " indptr", A.indptr.itemsize)

    i = names.index("budget_2028")
    start, end = A.indptr[i], A.indptr[i + 1]
    print(f"row {i} ({names[i]}): positions {start}..{end - 1}")
    for j, a in zip(A.indices[start:end], A.data[start:end]):
        print(f"  {tiny.project_ids[j]}: {a}")

from __future__ import annotations


def to_csr(n_rows: int, triplets: list[tuple[int, int, float]]) -> tuple[list[int], list[int], list[float]]:
    """CSR arrays (indptr, indices, data) of an n_rows-row matrix given as (row, col, value) triplets."""
    merged: dict[tuple[int, int], float] = {}
    for r, c, v in triplets:
        merged[r, c] = merged.get((r, c), 0) + v
    indptr, indices, data = [0], [], []
    for r in range(n_rows):
        for row, col in sorted(k for k in merged if k[0] == r):
            indices.append(col)
            data.append(merged[row, col])
        indptr.append(len(data))
    return indptr, indices, data


if __name__ == "__main__":
    print(to_csr(2, [(0, 1, 5), (1, 0, 2), (0, 0, 3)]))

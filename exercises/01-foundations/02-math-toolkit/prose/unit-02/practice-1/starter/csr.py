from __future__ import annotations


def to_csr(n_rows: int, triplets: list[tuple[int, int, float]]) -> tuple[list[int], list[int], list[float]]:
    """CSR arrays (indptr, indices, data) of an n_rows-row matrix given as (row, col, value) triplets."""
    # TODO: group the triplets by row, sort each row by column, and record where each row ends.
    return [0] * (n_rows + 1), [], []


if __name__ == "__main__":
    print(to_csr(2, [(0, 1, 5), (1, 0, 2), (0, 0, 3)]))

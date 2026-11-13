from __future__ import annotations


def csr_activity(indptr: list[int], indices: list[int], data: list[float], x: list[float]) -> list[float]:
    """Each row's activity, row @ x, read from CSR arrays without forming the dense matrix."""
    # TODO: one sum per row, over that row's slice of data.
    return [-1.0 for _ in range(len(indptr) - 1)]


if __name__ == "__main__":
    print(csr_activity([0, 2, 3], [0, 2, 1], [1.0, 2.0, 5.0], [1.0, 1.0, 1.0]))

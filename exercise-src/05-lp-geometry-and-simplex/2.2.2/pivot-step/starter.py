from __future__ import annotations


def pivot(T: list[list[float]], r: int, k: int) -> list[list[float]]:
    """The tableau after pivoting on row r and column k. T itself is left unchanged."""
    # TODO: divide row r by T[r][k]; from every other row i, objective row included, subtract
    # T[i][k] times the new row r. Build a new tableau rather than changing T.
    return [list(row) for row in T]


if __name__ == "__main__":
    T = [[1, 1, 1, 0, 5],
         [2, 1, 0, 1, 8],
         [-3, -2, 0, 0, 0]]
    for row in pivot(T, 1, 0):
        print(row)

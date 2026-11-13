from __future__ import annotations


def pivot(T: list[list[float]], r: int, k: int) -> list[list[float]]:
    """The tableau after pivoting on row r and column k. T itself is left unchanged."""
    result = [list(row) for row in T]
    result[r] = [v / T[r][k] for v in T[r]]
    for i in range(len(T)):
        if i != r:
            f = T[i][k]
            result[i] = [v - f * w for v, w in zip(T[i], result[r])]
    return result


if __name__ == "__main__":
    T = [[1, 1, 1, 0, 5],
         [2, 1, 0, 1, 8],
         [-3, -2, 0, 0, 0]]
    for row in pivot(T, 1, 0):
        print(row)

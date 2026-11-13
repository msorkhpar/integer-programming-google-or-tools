from __future__ import annotations

EPS = 1e-9


def choose_pivot(T: list[list[float]]) -> tuple[int, int] | None:
    """The (row, column) of the next pivot by Dantzig's rule and the ratio test, or None at an optimum."""
    z = T[-1][:-1]
    k = min(range(len(z)), key=lambda j: z[j])
    if z[k] >= -EPS:
        return None
    best = None
    for i in range(len(T) - 1):
        if T[i][k] > EPS:
            ratio = T[i][-1] / T[i][k]
            if best is None or ratio < best[0]:
                best = (ratio, i)
    return best[1], k


if __name__ == "__main__":
    T = [[1, 1, 1, 0, 5],
         [2, 1, 0, 1, 8],
         [-3, -2, 0, 0, 0]]
    print(choose_pivot(T))

from __future__ import annotations

EPS = 1e-9


def pivot(T: list[list[float]], r: int, k: int) -> list[list[float]]:
    row = [v / T[r][k] for v in T[r]]
    return [row if i == r else [v - T[i][k] * w for v, w in zip(T[i], row)] for i in range(len(T))]


def entering(T: list[list[float]]) -> int | None:
    z = T[-1][:-1]
    k = min(range(len(z)), key=lambda j: z[j])
    return k if z[k] < -EPS else None


def ratio_row(T: list[list[float]], k: int) -> int | None:
    """The leaving row for column k by the ratio test, or None when no row limits k."""
    best = None
    for i in range(len(T) - 1):
        if T[i][k] > EPS:
            ratio = T[i][-1] / T[i][k]
            if best is None or ratio < best[0]:
                best = (ratio, i)
    return None if best is None else best[1]


def run_simplex(T: list[list[float]], max_steps: int = 100) -> tuple[str, float | None]:
    """Pivot until optimal or unbounded: ("OPTIMAL", value) or ("UNBOUNDED", None)."""
    for _ in range(max_steps):
        k = entering(T)
        if k is None:
            return "OPTIMAL", T[-1][-1]
        r = ratio_row(T, k)
        if r is None:
            return "UNBOUNDED", None
        T = pivot(T, r, k)
    return "STEP_LIMIT", None


if __name__ == "__main__":
    print(run_simplex([[1, 1, 1, 0, 5], [2, 1, 0, 1, 8], [-3, -2, 0, 0, 0]]))
    print(run_simplex([[1, -1, 1, 2], [-1, -2, 0, 0]]))

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
    # TODO: the smallest rhs / entry over constraint rows whose entry is above EPS (lowest row on a
    # tie); None when no row has a positive entry.
    return None


def run_simplex(T: list[list[float]], max_steps: int = 100) -> tuple[str, float | None]:
    """Pivot until optimal or unbounded: ("OPTIMAL", value) or ("UNBOUNDED", None)."""
    # TODO: loop up to max_steps: entering column (None means optimal), ratio row (None means
    # unbounded), pivot. Return ("STEP_LIMIT", None) if the loop runs out.
    return "NOT_RUN", 0.0


if __name__ == "__main__":
    print(run_simplex([[1, 1, 1, 0, 5], [2, 1, 0, 1, 8], [-3, -2, 0, 0, 0]]))
    print(run_simplex([[1, -1, 1, 2], [-1, -2, 0, 0]]))

from __future__ import annotations


def reduced_costs(c: list[float], A: list[list[float]], pi: list[float]) -> list[float]:
    """RC_j = c_j - sum_i A[i][j] * pi[i], one per column."""
    # TODO: one sum per column, over every row.
    return [0.0 for _ in c]


def wrong_signs(rc: list[float], where: list[str], maximize: bool, tol: float = 1e-9) -> list[int]:
    """Indices of the variables whose reduced cost breaks the sign rule for where they sit."""
    # TODO: a basic variable needs RC = 0; at a bound, the sign depends on the bound and the sense.
    return [-1]


if __name__ == "__main__":
    rc = reduced_costs([3.0, 5.0], [[1.0, 0.0], [0.0, 2.0], [3.0, 2.0]], [0.0, 1.5, 1.0])
    print(rc, wrong_signs(rc, ["basic", "basic"], maximize=True))

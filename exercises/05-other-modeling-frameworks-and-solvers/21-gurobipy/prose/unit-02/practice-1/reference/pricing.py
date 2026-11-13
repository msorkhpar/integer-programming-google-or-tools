from __future__ import annotations


def reduced_costs(c: list[float], A: list[list[float]], pi: list[float]) -> list[float]:
    """RC_j = c_j - sum_i A[i][j] * pi[i], one per column."""
    return [c[j] - sum(row[j] * p for row, p in zip(A, pi)) for j in range(len(c))]


def wrong_signs(rc: list[float], where: list[str], maximize: bool, tol: float = 1e-9) -> list[int]:
    """Indices of the variables whose reduced cost breaks the sign rule for where they sit."""
    bad = []
    for j, (r, w) in enumerate(zip(rc, where)):
        signed = r if maximize else -r          # a minimization's rules are the maximization's, negated
        if w == "basic" and abs(r) > tol:
            bad.append(j)
        elif w == "lower" and signed > tol:
            bad.append(j)
        elif w == "upper" and signed < -tol:
            bad.append(j)
    return sorted(bad)


if __name__ == "__main__":
    rc = reduced_costs([3.0, 5.0], [[1.0, 0.0], [0.0, 2.0], [3.0, 2.0]], [0.0, 1.5, 1.0])
    print(rc, wrong_signs(rc, ["basic", "basic"], maximize=True))

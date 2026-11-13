from __future__ import annotations

EPS = 1e-9


def tighten(coefs: dict[str, float], rhs: float) -> tuple[dict[str, float], float]:
    """Coefficient tightening of  sum a_j x_j <= rhs  over free binaries with a_j > 0."""
    # TODO: for each variable in sorted order, d = rhs - (sum of the current coefficients - a_k);
    # when d > EPS lower a_k and rhs by d. Work on a copy.
    return dict(coefs), rhs


if __name__ == "__main__":
    print(tighten({"a": 4, "b": 3, "c": 3}, 8))

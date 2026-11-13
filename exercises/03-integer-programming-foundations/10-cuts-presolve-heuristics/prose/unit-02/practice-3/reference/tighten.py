from __future__ import annotations

EPS = 1e-9


def tighten(coefs: dict[str, float], rhs: float) -> tuple[dict[str, float], float]:
    """Coefficient tightening of  sum a_j x_j <= rhs  over free binaries with a_j > 0."""
    new = dict(coefs)
    for k in sorted(new):
        most = sum(new.values())
        d = rhs - (most - new[k])
        if d > EPS:
            new[k] -= d
            rhs -= d
    return new, rhs


if __name__ == "__main__":
    print(tighten({"a": 4, "b": 3, "c": 3}, 8))

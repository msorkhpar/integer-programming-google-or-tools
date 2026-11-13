from __future__ import annotations


def fits(n_vars: int, n_rows: int, quadratic: bool, tier: dict[str, tuple]) -> bool:
    """Whether a model with these counts is within the tier's caps (None: no cap on that count)."""
    max_vars, max_rows, max_sum = tier["quadratic" if quadratic else "linear"]
    return ((max_vars is None or n_vars <= max_vars)
            and (max_rows is None or n_rows <= max_rows)
            and (max_sum is None or n_vars + n_rows <= max_sum))


if __name__ == "__main__":
    tier = {"linear": (2000, 2000, None), "quadratic": (200, 2000, None)}
    print(fits(887, 469, False, tier), fits(887, 469, True, tier))

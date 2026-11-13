from __future__ import annotations


def fits(n_vars: int, n_rows: int, quadratic: bool, tier: dict[str, tuple]) -> bool:
    """Whether a model with these counts is within the tier's caps (None: no cap on that count)."""
    # TODO: pick the caps for the model's kind, then check each count that has a cap.
    return False


if __name__ == "__main__":
    tier = {"linear": (2000, 2000, None), "quadratic": (200, 2000, None)}
    print(fits(887, 469, False, tier), fits(887, 469, True, tier))

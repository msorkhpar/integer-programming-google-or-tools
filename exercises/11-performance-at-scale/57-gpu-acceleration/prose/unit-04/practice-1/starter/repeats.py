from __future__ import annotations

SAME = ("inputs", "device", "solver", "method", "threads", "tolerance", "versions")


def bits_promised(a: dict, b: dict) -> bool:
    """True when run b repeats run a's configuration exactly and that configuration repeats bit for bit."""
    # TODO: the same configuration, and one that repeats.
    return False


def verdict(a: dict, b: dict, tol: float) -> str:
    """'identical', 'within tolerance', 'different' or 'not comparable'."""
    # TODO: inputs first, then bits where they were promised, else the tolerance.
    return ""


if __name__ == "__main__":
    run = {"inputs": "lp-7", "device": "cpu", "solver": "highs", "method": "simplex", "threads": 1, "tolerance": 1e-7,
           "versions": "1.14.0", "kind": "lp", "objective": 10.0, "digest": "ab"}
    print(verdict(run, dict(run), 1e-6))

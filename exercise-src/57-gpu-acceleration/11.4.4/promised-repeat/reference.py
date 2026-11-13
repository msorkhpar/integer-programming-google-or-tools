from __future__ import annotations

SAME = ("inputs", "device", "solver", "method", "threads", "tolerance", "versions")


def bits_promised(a: dict, b: dict) -> bool:
    """True when run b repeats run a's configuration exactly and that configuration repeats bit for bit."""
    if any(a[k] != b[k] for k in SAME):
        return False
    if a["method"] == "concurrent":                  # a race: the winner can change between runs
        return False
    if a["solver"] == "cuopt" and a["kind"] == "milp":   # cuOpt MILP plans did not repeat with any setting
        return False
    return True


def verdict(a: dict, b: dict, tol: float) -> str:
    """'identical', 'within tolerance', 'different' or 'not comparable'."""
    if a["inputs"] != b["inputs"]:
        return "not comparable"
    if bits_promised(a, b):
        return "identical" if (a["digest"], a["objective"]) == (b["digest"], b["objective"]) else "different"
    close = abs(a["objective"] - b["objective"]) <= tol * max(1.0, abs(a["objective"]))
    return "within tolerance" if close else "different"


if __name__ == "__main__":
    run = {"inputs": "lp-7", "device": "cpu", "solver": "highs", "method": "simplex", "threads": 1, "tolerance": 1e-7,
           "versions": "1.14.0", "kind": "lp", "objective": 10.0, "digest": "ab"}
    print(verdict(run, dict(run), 1e-6))

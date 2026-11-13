from __future__ import annotations


def verdict(first: dict, second: dict, tol: float = 1e-6) -> str:
    """'same', 'tie' or 'different' for two runs of the same model."""
    if first["status"] != second["status"] or abs(first["objective"] - second["objective"]) > tol:
        return "different"
    return "same" if first["plan"] == second["plan"] else "tie"


if __name__ == "__main__":
    run = {"status": "OPTIMAL", "objective": 41.0, "plan": {"S1": "T2", "S2": "T1"}}
    print(verdict(run, run))

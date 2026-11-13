from __future__ import annotations

# A switched rule: sum(coef * value of var) <= limit, unless the switch variable is on.
# rows = [{"name": str, "terms": {var name: coef}, "limit": float, "switch": var name}, ...]
# values = {var name: value the solver returned}


def leaks(values: dict[str, float], rows: list[dict], tol: float = 1e-6) -> list[str]:
    """Names of the rows broken while their switch counts as off, in the order given."""
    broken = []
    for row in rows:
        total = sum(coef * values[var] for var, coef in row["terms"].items())
        switched_off = values[row["switch"]] < 0.5
        if switched_off and total > row["limit"] + tol:
            broken.append(row["name"])
    return broken


if __name__ == "__main__":
    rows = [{"name": "berth_1", "terms": {"ship_a": 4, "ship_b": 3}, "limit": 6, "switch": "tug_1"}]
    print(leaks({"ship_a": 1, "ship_b": 1, "tug_1": 7e-7}, rows))

from __future__ import annotations


def where_it_stops(trace: list[dict], limits: dict) -> tuple[int | None, str | None]:
    """The first row of a maximization's trace at which a stopping rule is met, and the rule."""
    for index, row in enumerate(trace):
        incumbent = row["incumbent"]
        if incumbent is not None:
            absolute = row["bound"] - incumbent
            relative = absolute / abs(incumbent)
            if "relative_gap" in limits and relative <= limits["relative_gap"]:
                return index, "relative_gap"
            if "absolute_gap" in limits and absolute <= limits["absolute_gap"]:
                return index, "absolute_gap"
        if "nodes" in limits and row["nodes"] >= limits["nodes"]:
            return index, "nodes"
        if "solutions" in limits and row["solutions"] >= limits["solutions"]:
            return index, "solutions"
        if "seconds" in limits and row["seconds"] >= limits["seconds"]:
            return index, "seconds"
    return None, None


if __name__ == "__main__":
    trace = [
        {"seconds": 0.2, "nodes": 0, "solutions": 1, "incumbent": 80.0, "bound": 100.0},
        {"seconds": 3.0, "nodes": 120, "solutions": 3, "incumbent": 95.0, "bound": 99.0},
    ]
    print(where_it_stops(trace, {"relative_gap": 0.05, "seconds": 60}))

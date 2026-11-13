from __future__ import annotations


def where_it_stops(trace: list[dict], limits: dict) -> tuple[int | None, str | None]:
    """The first row of a maximization's trace at which a stopping rule is met, and the rule."""
    # TODO: walk the rows in order and check each rule in `limits` on each row.
    return -1, ""


if __name__ == "__main__":
    trace = [
        {"seconds": 0.2, "nodes": 0, "solutions": 1, "incumbent": 80.0, "bound": 100.0},
        {"seconds": 3.0, "nodes": 120, "solutions": 3, "incumbent": 95.0, "bound": 99.0},
    ]
    print(where_it_stops(trace, {"relative_gap": 0.05, "seconds": 60}))

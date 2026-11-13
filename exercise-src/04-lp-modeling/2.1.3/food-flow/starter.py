from __future__ import annotations

from ortools.math_opt.python import mathopt

Arc = tuple[str, str]


def ship(supply: dict[str, float], demand: dict[str, float], arcs: dict[Arc, tuple[float, float]]):
    """Cheapest flow meeting every demand. Returns (status, cost, flow by arc)."""
    # TODO: one flow variable per arc, one row per node, the cost, a GLOP solve, the status first.
    return "NOT_SOLVED", None, None

if __name__ == "__main__":
    print(ship({"W1": 10}, {"P1": 10}, {("W1", "P1"): (3, 20)}))

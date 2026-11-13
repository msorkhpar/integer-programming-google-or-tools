from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Row:
    name: str
    coefs: dict[str, float]     # variable -> coefficient
    sense: str                  # "<=", ">=" or "=="
    rhs: float


def slack(row: Row, plan: dict[str, float]) -> float:
    """Room left at the plan: >= 0 when the row holds, 0 when it binds, < 0 when it is broken."""
    # TODO: the activity of the row at the plan, then the room left, by the row's sense.
    return 0.0


def binding(rows: list[Row], plan: dict[str, float], tol: float = 1e-6) -> list[str]:
    """Names of the rows the plan keeps with no slack left, in the order given."""
    # TODO: use slack().
    return []


if __name__ == "__main__":
    depot = Row("depot_space", {"bus_a": 12, "bus_b": 9}, "<=", 40)
    print(slack(depot, {"bus_a": 2, "bus_b": 1}))

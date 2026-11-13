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
    activity = sum(c * plan.get(var, 0.0) for var, c in row.coefs.items())
    if row.sense == "<=":
        return row.rhs - activity
    if row.sense == ">=":
        return activity - row.rhs
    return -abs(activity - row.rhs)


def binding(rows: list[Row], plan: dict[str, float], tol: float = 1e-6) -> list[str]:
    """Names of the rows the plan keeps with no slack left, in the order given."""
    return [row.name for row in rows if abs(slack(row, plan)) <= tol]


if __name__ == "__main__":
    depot = Row("depot_space", {"bus_a": 12, "bus_b": 9}, "<=", 40)
    print(slack(depot, {"bus_a": 2, "bus_b": 1}))

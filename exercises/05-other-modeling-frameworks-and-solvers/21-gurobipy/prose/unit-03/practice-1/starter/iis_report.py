from __future__ import annotations

from gurobipy import GRB


def iis_report(status: int, rows: list[dict], bounds: list[dict]) -> list[str]:
    """Sorted lines, one per row and per variable bound that computeIIS marked."""
    # TODO: check the status, then map each marked row's sense to an operator, then the bounds.
    return ["no conflict"]


if __name__ == "__main__":
    rows = [{"name": "night_cover", "sense": ">", "rhs": 6.0, "iis": 1},
            {"name": "staff_hours", "sense": "<", "rhs": 160.0, "iis": 1}]
    print(iis_report(GRB.INFEASIBLE, rows, []))

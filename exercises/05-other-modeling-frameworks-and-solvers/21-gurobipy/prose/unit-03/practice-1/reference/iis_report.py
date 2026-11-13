from __future__ import annotations

from gurobipy import GRB

OPERATOR = {"<": "<=", ">": ">=", "=": "=="}


def iis_report(status: int, rows: list[dict], bounds: list[dict]) -> list[str]:
    """Sorted lines, one per row and per variable bound that computeIIS marked."""
    if status != GRB.INFEASIBLE:
        return []
    lines = [f"{r['name']} {OPERATOR[r['sense']]} {r['rhs']:g}" for r in rows if r["iis"]]
    for v in bounds:
        if v["iis_lb"]:
            lines.append(f"{v['name']} >= {v['lb']:g}")
        if v["iis_ub"]:
            lines.append(f"{v['name']} <= {v['ub']:g}")
    return sorted(lines)


if __name__ == "__main__":
    rows = [{"name": "night_cover", "sense": ">", "rhs": 6.0, "iis": 1},
            {"name": "staff_hours", "sense": "<", "rhs": 160.0, "iis": 1}]
    print(iis_report(GRB.INFEASIBLE, rows, []))

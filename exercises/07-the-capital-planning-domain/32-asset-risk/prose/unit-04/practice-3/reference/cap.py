from ortools.math_opt.python import mathopt


def add_risk_caps(model: mathopt.Model, x: dict, base: dict, cut: dict, cap: dict) -> dict:
    """In every year, the risk left after the plan's projects is at most that year's cap."""
    rows = {}
    for y in sorted(cap):
        remaining = base[y] - sum(cut[key][y] * var for key, var in x.items())
        rows[y] = model.add_linear_constraint(remaining <= cap[y], name=f"risk_cap_{y}")
    return rows

from ortools.math_opt.python import mathopt


def add_risk_caps(model: mathopt.Model, x: dict, base: dict, cut: dict, cap: dict) -> dict:
    """In every year, the risk left after the plan's projects is at most that year's cap."""
    rows = {}
    # TODO: one row per year.
    return rows

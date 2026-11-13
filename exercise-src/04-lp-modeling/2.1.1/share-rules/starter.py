from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_share_rules(model: mathopt.Model, spend: dict[str, mathopt.Variable], max_share: float,
                    pairs: list[tuple[str, str, float]]) -> None:
    """Add the agency's ratio rules to `model` as linear rows."""
    # TODO: one share row per mode, then one row per (a, b, ratio) pair, each multiplied out.
    return None

if __name__ == "__main__":
    model = mathopt.Model()
    spend = {k: model.add_variable(lb=0, name=k) for k in ("bus", "rail", "ferry")}
    add_share_rules(model, spend, 0.5, [("rail", "ferry", 2.0)])
    for row in model.linear_constraints():
        print(row.name, row.lower_bound, row.upper_bound)

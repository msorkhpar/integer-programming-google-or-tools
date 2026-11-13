from __future__ import annotations

from ortools.sat.python import cp_model


def add_tier_flag(model: cp_model.CpModel, spend, gold, threshold: int) -> None:
    """gold is true exactly when spend reaches the threshold."""
    # TODO: tie the flag to the spend, in both directions.
    return None

if __name__ == "__main__":
    model = cp_model.CpModel()
    spend = model.new_int_var(0, 1_000, "spend")
    gold = model.new_bool_var("gold")
    add_tier_flag(model, spend, gold, 500)
    model.add(spend == 650)
    solver = cp_model.CpSolver()
    solver.solve(model)
    print("gold:", solver.boolean_value(gold))

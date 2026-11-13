from __future__ import annotations

from ortools.sat.python import cp_model


def build(costs: dict[str, int], values: dict[str, int], must: set[str],
          budget: int) -> tuple[cp_model.CpModel, dict[str, cp_model.IntVar]]:
    """Given: this year's model. pick[p] = 1 funds project p."""
    model = cp_model.CpModel()
    pick = {p: model.new_bool_var(f"pick_{p}") for p in costs}
    model.add(sum(costs[p] * pick[p] for p in costs) <= budget)
    for p in must:
        model.add(pick[p] == 1)
    model.maximize(sum(values[p] * pick[p] for p in costs))
    return model, pick


def add_plan_hint(model: cp_model.CpModel, pick: dict[str, cp_model.IntVar], plan: set[str]) -> None:
    """Hint the plan: 1 for every project it funds, 0 for every other project."""
    # TODO: one hint per project.
    return None


def fits(costs: dict[str, int], values: dict[str, int], must: set[str], budget: int, plan: set[str]) -> bool:
    """Does last year's plan keep every rule of this year's model?"""
    # TODO: hint the plan, fix every variable to its hint, solve with one worker.
    return False


if __name__ == "__main__":
    costs, values = {"A": 40, "B": 30, "C": 50}, {"A": 70, "B": 60, "C": 50}
    print(fits(costs, values, {"C"}, 90, {"A", "C"}), fits(costs, values, {"C"}, 90, {"A", "B"}))

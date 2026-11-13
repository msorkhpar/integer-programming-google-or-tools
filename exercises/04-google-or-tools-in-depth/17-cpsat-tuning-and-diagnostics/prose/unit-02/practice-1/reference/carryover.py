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
    for p, var in pick.items():
        model.add_hint(var, 1 if p in plan else 0)


def fits(costs: dict[str, int], values: dict[str, int], must: set[str], budget: int, plan: set[str]) -> bool:
    """Does last year's plan keep every rule of this year's model?"""
    model, pick = build(costs, values, must, budget)
    add_plan_hint(model, pick, plan)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.fix_variables_to_their_hinted_value = True
    status = solver.solve(model)
    return status in (cp_model.OPTIMAL, cp_model.FEASIBLE)


if __name__ == "__main__":
    costs, values = {"A": 40, "B": 30, "C": 50}, {"A": 70, "B": 60, "C": 50}
    print(fits(costs, values, {"C"}, 90, {"A", "C"}), fits(costs, values, {"C"}, 90, {"A", "B"}))

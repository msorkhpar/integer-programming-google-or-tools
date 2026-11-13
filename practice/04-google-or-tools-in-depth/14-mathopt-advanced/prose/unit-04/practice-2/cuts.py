from __future__ import annotations

from ortools.math_opt.python import mathopt


def cut_table(model: mathopt.Model, budget_row, cuts: list[float]) -> list[float]:
    """The optimum for each relative cut of the budget row's current limit; the model is left as it was."""
    # TODO: one IncrementalSolver, one edit and one solve per cut, then put the limit back.
    return []


def build(repairs: dict[str, tuple[float, float]], budget: float):
    """repairs: name -> (value, cost)."""
    model = mathopt.Model(name="repairs")
    x = {r: model.add_binary_variable(name=f"x_{r}") for r in repairs}
    row = model.add_linear_constraint(sum(repairs[r][1] * x[r] for r in repairs) <= budget, name="budget")
    model.maximize(sum(repairs[r][0] * x[r] for r in repairs))
    return model, x, row


if __name__ == "__main__":
    model, x, row = build({"roof": (9, 6), "boiler": (7, 5), "windows": (4, 3)}, 10)
    print(cut_table(model, row, [0.0, 0.2]))

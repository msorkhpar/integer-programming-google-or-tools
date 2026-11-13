from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_yearly_budgets(model: mathopt.Model, spend: dict, budgets: dict[int, int]) -> None:
    """The old rule: each year's spend within that year's budget."""
    for year, budget in budgets.items():
        model.add_linear_constraint(spend[year] <= budget, name=f"budget_{year}")


def add_advances(model: mathopt.Model, spend: dict, budgets: dict[int, int], max_advance: float) -> dict:
    """Let each year spend early up to `max_advance` of the next year's budget."""
    # TODO: write the formulation first, then its variables and rows. Return the advance variables by year.
    return {}


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_binary_variable(name="water_main")
    spend = {2027: 300 * x, 2028: 0 * x}
    print(add_advances(model, spend, {2027: 250, 2028: 250}, 0.2))

from __future__ import annotations

from ortools.math_opt.python import mathopt


def spend_variables(model: mathopt.Model, items: dict[str, tuple[float, float]]) -> dict:
    """One continuous spend variable per work order, with its (lowest, highest) spend in $k."""
    return {name: model.add_variable(lb=lo, ub=hi, name=f"spend_{name}") for name, (lo, hi) in items.items()}


def add_floor(model: mathopt.Model, spend: dict, floor: float, waiver: mathopt.Variable) -> None:
    """The district's total spend is at least `floor`, unless `waiver` is 1."""
    # TODO: your row, with the smallest M the variables' bounds allow.
    return None


if __name__ == "__main__":
    model = mathopt.Model()
    spend = spend_variables(model, {"trim": (0, 60), "poles": (20, 80)})
    waiver = model.add_binary_variable(name="waiver")
    add_floor(model, spend, 100, waiver)
    print(model.get_num_linear_constraints(), "row")

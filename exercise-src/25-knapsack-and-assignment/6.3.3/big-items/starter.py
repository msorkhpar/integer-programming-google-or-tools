from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Limit:
    name: str
    use: dict          # job -> how much of this resource it uses (whole numbers)
    capacity: int


def add_big_item_rows(model: mathopt.Model, x: dict, limits: list[Limit]) -> None:
    """Valid rows from the jobs too big to share a resource: at most one of them, none if alone too big."""
    # TODO: the valid rows that pairs of big jobs give.
    return None

def build(values: dict, limits: list[Limit], *, integer: bool = True) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="substation-jobs")
    x = {j: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{j}") for j in values}
    for lim in limits:
        model.add_linear_constraint(sum(u * x[j] for j, u in lim.use.items()) <= lim.capacity, name=lim.name)
    add_big_item_rows(model, x, limits)
    model.maximize(sum(v * x[j] for j, v in values.items()))
    return model, x


if __name__ == "__main__":
    limits = [Limit("crane", {"J1": 7, "J2": 6, "J3": 2}, 10)]
    model, x = build({"J1": 5, "J2": 4, "J3": 1}, limits, integer=False)
    print(len(list(model.linear_constraints())), "rows")

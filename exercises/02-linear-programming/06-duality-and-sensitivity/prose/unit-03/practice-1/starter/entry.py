from __future__ import annotations

from ortools.math_opt.python import mathopt


def entry_values(model: mathopt.Model, tol: float = 1e-9) -> dict[str, float]:
    """For each variable the optimal plan leaves at 0: the objective coefficient at which it starts to pay."""
    # TODO: solve with GLOP; for every variable at 0, read its coefficient and its reduced cost.
    return {}


if __name__ == "__main__":
    model = mathopt.Model()
    roofs = model.add_variable(lb=0, name="roofs")
    paint = model.add_variable(lb=0, name="paint")
    model.add_linear_constraint(roofs + paint <= 100, name="budget")
    model.maximize(0.6 * roofs + 0.2 * paint)
    print(entry_values(model))

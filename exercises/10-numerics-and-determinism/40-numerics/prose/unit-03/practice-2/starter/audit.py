from __future__ import annotations

from ortools.math_opt.python import mathopt


def audit(model: mathopt.Model, values: dict) -> dict[str, float]:
    """The largest bound, integrality and row violation of `values`, as HiGHS's report prints them."""
    # TODO: measure each kind of violation; 0.0 when there is none.
    return {"bound": -1.0, "integrality": -1.0, "row": -1.0}


if __name__ == "__main__":
    model = mathopt.Model()
    depot = model.add_binary_variable(name="open_north")
    model.add_linear_constraint(depot <= 1, name="once")
    print(audit(model, {depot: 0.9999996}))

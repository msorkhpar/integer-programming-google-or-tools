from __future__ import annotations

from ortools.math_opt.python import mathopt


def audit(model: mathopt.Model, values: dict) -> dict[str, float]:
    """The largest bound, integrality and row violation of `values`, as HiGHS's report prints them."""
    worst = {"bound": 0.0, "integrality": 0.0, "row": 0.0}
    for var in model.variables():
        v = values[var]
        worst["bound"] = max(worst["bound"], var.lower_bound - v, v - var.upper_bound)
        if var.integer:
            worst["integrality"] = max(worst["integrality"], abs(v - round(v)))
    for row in model.linear_constraints():
        activity = sum(row.get_coefficient(var) * values[var] for var in model.row_nonzeros(row))
        worst["row"] = max(worst["row"], row.lower_bound - activity, activity - row.upper_bound)
    return worst


if __name__ == "__main__":
    model = mathopt.Model()
    depot = model.add_binary_variable(name="open_north")
    model.add_linear_constraint(depot <= 1, name="once")
    print(audit(model, {depot: 0.9999996}))

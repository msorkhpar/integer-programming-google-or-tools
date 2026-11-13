from __future__ import annotations

from ortools.math_opt.python import mathopt


def replace_upper(model: mathopt.Model, ic, new_upper: float):
    """Delete `ic` and add the same indicator constraint with upper bound `new_upper`; return the new one."""
    # TODO: read the parts, delete, add again.
    return ic


if __name__ == "__main__":
    model = mathopt.Model()
    z, heat = model.add_binary_variable(name="z"), model.add_variable(lb=0, ub=200, name="heat")
    ic = model.add_indicator_constraint(indicator=z, implied_constraint=(40 <= heat) <= 120, name="boiler")
    print(replace_upper(model, ic, 100).upper_bound)

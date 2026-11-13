from __future__ import annotations

from ortools.math_opt.python import mathopt


def replace_upper(model: mathopt.Model, ic, new_upper: float):
    """Delete `ic` and add the same indicator constraint with upper bound `new_upper`; return the new one."""
    indicator, on_zero, name = ic.indicator_variable, ic.activate_on_zero, ic.name
    lower = ic.lower_bound
    expr = mathopt.fast_sum(term.coefficient * term.variable for term in ic.terms())
    model.delete_indicator_constraint(ic)
    return model.add_indicator_constraint(indicator=indicator, activate_on_zero=on_zero, implied_expr=expr,
                                          implied_lb=lower, implied_ub=new_upper, name=name)


if __name__ == "__main__":
    model = mathopt.Model()
    z, heat = model.add_binary_variable(name="z"), model.add_variable(lb=0, ub=200, name="heat")
    ic = model.add_indicator_constraint(indicator=z, implied_constraint=(40 <= heat) <= 120, name="boiler")
    print(replace_upper(model, ic, 100).upper_bound)

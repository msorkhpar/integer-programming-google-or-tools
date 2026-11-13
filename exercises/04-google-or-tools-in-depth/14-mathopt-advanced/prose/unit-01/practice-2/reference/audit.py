from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def audit(model: mathopt.Model) -> list[tuple]:
    """(name, indicator name, active value, lower, upper, {variable name: coefficient}) per indicator."""
    rows = []
    for ic in model.get_indicator_constraints():
        rows.append((ic.name, ic.indicator_variable.name, 0 if ic.activate_on_zero else 1,
                     ic.lower_bound, ic.upper_bound,
                     {term.variable.name: term.coefficient for term in ic.terms()}))
    return rows


if __name__ == "__main__":
    model = mathopt.Model()
    z, a, b = model.add_binary_variable(name="z"), model.add_variable(name="a"), model.add_variable(name="b")
    model.add_indicator_constraint(indicator=z, implied_constraint=2 * a + 3 * b <= 10, name="cap")
    print(audit(model), math.inf)

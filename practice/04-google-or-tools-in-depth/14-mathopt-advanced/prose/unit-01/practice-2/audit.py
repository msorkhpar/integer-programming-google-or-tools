from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def audit(model: mathopt.Model) -> list[tuple]:
    """(name, indicator name, active value, lower, upper, {variable name: coefficient}) per indicator."""
    # TODO: read each indicator constraint's properties.
    return []


if __name__ == "__main__":
    model = mathopt.Model()
    z, a, b = model.add_binary_variable(name="z"), model.add_variable(name="a"), model.add_variable(name="b")
    model.add_indicator_constraint(indicator=z, implied_constraint=2 * a + 3 * b <= 10, name="cap")
    print(audit(model), math.inf)

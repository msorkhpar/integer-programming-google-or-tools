from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def describe(row: mathopt.LinearConstraint) -> str:
    """One line for one row: 'name: terms <= ub', '>= lb', '== value' or 'lb <= terms <= ub'."""
    # TODO: read the row's name, bounds and terms.
    return ""


def describe_model(model: mathopt.Model) -> list[str]:
    """Every row of the model, in creation order."""
    # TODO: one line per row.
    return []


if __name__ == "__main__":
    model = mathopt.Model(name="buses")
    a, b = model.add_binary_variable(name="x_a"), model.add_binary_variable(name="x_b")
    model.add_linear_constraint(3 * a + 2 * b <= 10, name="budget")
    print("\n".join(describe_model(model)))

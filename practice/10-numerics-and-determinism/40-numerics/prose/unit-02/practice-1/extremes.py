from __future__ import annotations

from ortools.math_opt.python import mathopt

Entry = tuple[str, str, float]


def matrix_extremes(model: mathopt.Model) -> tuple[Entry, Entry]:
    """The smallest and the largest matrix entry by absolute value, as (row, variable, coefficient)."""
    # TODO: look at every nonzero coefficient of every row.
    return ("", "", 0.0), ("", "", 0.0)


if __name__ == "__main__":
    model = mathopt.Model()
    nurses = model.add_variable(lb=0, name="nurses")
    model.add_linear_constraint(0.0001 * nurses <= 3, name="tiny")
    model.add_linear_constraint(1e8 * nurses <= 5e9, name="huge")
    print(matrix_extremes(model))

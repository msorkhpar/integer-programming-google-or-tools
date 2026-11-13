from __future__ import annotations

from ortools.math_opt.python import mathopt

Entry = tuple[str, str, float]


def matrix_extremes(model: mathopt.Model) -> tuple[Entry, Entry]:
    """The smallest and the largest matrix entry by absolute value, as (row, variable, coefficient)."""
    entries = [(row.name, var.name, row.get_coefficient(var))
               for row in model.linear_constraints() for var in model.row_nonzeros(row)]
    smallest = min(entries, key=lambda e: abs(e[2]))
    largest = max(entries, key=lambda e: abs(e[2]))
    return smallest, largest


if __name__ == "__main__":
    model = mathopt.Model()
    nurses = model.add_variable(lb=0, name="nurses")
    model.add_linear_constraint(0.0001 * nurses <= 3, name="tiny")
    model.add_linear_constraint(1e8 * nurses <= 5e9, name="huge")
    print(matrix_extremes(model))

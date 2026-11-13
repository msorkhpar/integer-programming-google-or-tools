from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def free_to_grow(model: mathopt.Model) -> list[str]:
    """Names of the variables the objective pushes in a direction that no bound and no row limits."""
    # TODO: for each variable, decide which way the objective pushes it, then whether a bound
    # or some row stops it going that way. Return the names of those nothing stops, sorted.
    return []


if __name__ == "__main__":
    model = mathopt.Model()
    order = model.add_variable(lb=0, name="order_gloves")
    refund = model.add_variable(lb=0, name="supplier_refund")
    model.add_linear_constraint(order <= 500, name="storage")
    model.maximize(2 * refund - order)
    print(free_to_grow(model))

from __future__ import annotations

from typing import Callable

from ortools.math_opt.python import mathopt


def audit(variants: dict[str, Callable[[bool], mathopt.Model]], optimum: float) -> list[dict]:
    """One line per formulation, in the order given: size, LP bound, root bound and share of gap closed.

    `variants[name](integer)` builds that formulation, as a MILP or (integer=False) as its LP
    relaxation. `optimum` is the best plan's value. The share of the gap closed is measured against
    the first variant, the one inherited.
    """
    # TODO: measure each variant.
    return []


if __name__ == "__main__":
    def one(integer):
        model = mathopt.Model()
        a = model.add_variable(lb=0, ub=1, is_integer=integer)
        model.add_linear_constraint(2 * a <= 1)
        model.maximize(a)
        return model

    print(audit({"only": one}, 0.0))

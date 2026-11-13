from __future__ import annotations

from typing import Callable

from ortools.math_opt.python import mathopt


def price_range(build: Callable[[float], tuple[mathopt.Model, mathopt.LinearConstraint]], rhs: float,
                low: float, high: float, tol: float = 1e-3) -> tuple[float, float]:
    """The interval of right-hand sides around `rhs`, inside [low, high], where the row keeps its price."""
    # TODO: the row's price at rhs; then, on each side, the farthest point that still has it.
    return rhs, rhs


if __name__ == "__main__":
    def build(r: float):
        model = mathopt.Model()
        x = model.add_variable(lb=0, ub=40, name="x")
        y = model.add_variable(lb=0, ub=30, name="y")
        row = model.add_linear_constraint(x + y <= r, name="budget")
        model.maximize(3 * x + 2 * y)
        return model, row

    print(price_range(build, 50, 0, 100))

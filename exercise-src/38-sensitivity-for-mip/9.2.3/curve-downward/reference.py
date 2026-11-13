from __future__ import annotations

from ortools.math_opt.python import mathopt

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def best(costs: list[int], values: list[int], budget: int) -> int:
    """V(budget): the best total value of renovations that fit the budget."""
    model = mathopt.Model()
    x = [model.add_binary_variable() for _ in costs]
    model.add_linear_constraint(sum(c * xi for c, xi in zip(costs, x)) <= budget)
    model.maximize(sum(v * xi for v, xi in zip(values, x)))
    return round(mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT).objective_value())


def cheapest(costs: list[int], values: list[int], level: int) -> int:
    """The least cost of any set of renovations worth at least `level`."""
    model = mathopt.Model()
    x = [model.add_binary_variable() for _ in costs]
    model.add_linear_constraint(sum(v * xi for v, xi in zip(values, x)) >= level)
    model.minimize(sum(c * xi for c, xi in zip(costs, x)))
    return round(mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT).objective_value())


def step_points(costs: list[int], values: list[int], lo: int, hi: int) -> list[tuple[int, int]]:
    """Every (budget, V(budget)) in [lo, hi] where V steps up, starting with (lo, V(lo)), found from hi downward."""
    points = []
    budget = hi
    while budget >= lo:
        value = best(costs, values, budget)            # the stretch this budget stands on
        start = cheapest(costs, values, value)         # where that stretch begins
        points.append((max(start, lo), value))
        budget = start - 1                             # the budget just below the stretch
    return points[::-1]


if __name__ == "__main__":
    print(step_points([3, 4, 6], [5, 7, 10], 0, 12))

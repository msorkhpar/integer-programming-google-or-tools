from __future__ import annotations

from ortools.math_opt.python import mathopt

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def sweep(costs: list[int], values: list[int], must: list[int], budgets: list[int]) -> list[tuple[int, int | None]]:
    """The best total value at each budget, or None where no plan meets the rules."""
    curve = []
    for b in budgets:
        model = mathopt.Model()
        x = [model.add_binary_variable(name=f"upgrade_{i}") for i in range(len(costs))]
        model.add_linear_constraint(sum(c * xi for c, xi in zip(costs, x)) <= b, name="budget")
        for i in must:
            model.add_linear_constraint(x[i] == 1, name=f"required_{i}")
        model.maximize(sum(v * xi for v, xi in zip(values, x)))
        result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT)
        if result.termination.reason == mathopt.TerminationReason.OPTIMAL:
            curve.append((b, round(result.objective_value())))
        else:
            curve.append((b, None))
    return curve


if __name__ == "__main__":
    print(sweep([2, 3, 4], [6, 6, 4], [], [0, 2, 5, 9]))

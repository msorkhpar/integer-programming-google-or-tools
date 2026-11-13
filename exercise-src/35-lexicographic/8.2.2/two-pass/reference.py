from __future__ import annotations

from ortools.math_opt.python import mathopt

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
TOL = 1e-6        # numerical slack on the kept row, as in lesson 8.2.2's lexicographic.py


def two_pass(model: mathopt.Model, first, second, *, first_max: bool, second_max: bool,
             abs_tol: float = 0.0, rel_tol: float = 0.0) -> tuple[float, float]:
    """(first, second) of the plan that optimizes `second` with `first` kept within its tolerance."""
    model.set_linear_objective(first, is_maximize=first_max)
    best = mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT).objective_value()
    loss = max(abs_tol, rel_tol * abs(best))
    if first_max:
        keep = model.add_linear_constraint(first >= best - loss - TOL)
    else:
        keep = model.add_linear_constraint(first <= best + loss + TOL)
    model.set_linear_objective(second, is_maximize=second_max)
    values = mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT).variable_values()
    model.delete_linear_constraint(keep)
    return mathopt.evaluate_expression(first, values), mathopt.evaluate_expression(second, values)


if __name__ == "__main__":
    model = mathopt.Model()
    x = [model.add_binary_variable(name=f"main_{i}") for i in range(3)]
    model.add_linear_constraint(4 * x[0] + 3 * x[1] + 2 * x[2] <= 6, name="budget")
    leaks, hours = 9 * x[0] + 7 * x[1] + 4 * x[2], 5 * x[0] + 6 * x[1] + 1 * x[2]
    print(two_pass(model, leaks, hours, first_max=True, second_max=False, rel_tol=0.1))

from __future__ import annotations

from ortools.math_opt.python import mathopt


def build() -> tuple[mathopt.Model, mathopt.LinearConstraint]:
    """The crew-hours LP. Given: you do not need to change it."""
    model = mathopt.Model(name="crews")
    a = model.add_variable(lb=0, ub=4, name="hours_A")
    b = model.add_variable(lb=0, ub=5, name="hours_B")
    c = model.add_variable(lb=0, ub=10, name="hours_C")
    budget = model.add_linear_constraint(2 * a + 2 * b + c <= 20, name="budget")
    model.maximize(6 * a + 5 * b + 2 * c)
    return model, budget


def what_if(model: mathopt.Model, row: mathopt.LinearConstraint, cut: float) -> tuple[float, float]:
    """Predict the objective after lowering `row`'s upper bound by `cut`, then re-solve to measure it.

    Returns (predicted, actual). The model is left as it was given.
    """
    base = mathopt.solve(model, mathopt.SolverType.GLOP)
    price = base.dual_values(row)
    predicted = base.objective_value() - price * cut
    before = row.upper_bound
    row.upper_bound = before - cut
    actual = mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()
    row.upper_bound = before
    return predicted, actual


if __name__ == "__main__":
    model, budget = build()
    for cut in (1, 6):
        print(cut, what_if(model, budget, cut))

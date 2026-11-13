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
    # TODO: solve the base model and read the row's dual value; predict; lower the bound by `cut`,
    # re-solve for the actual objective; put the bound back.
    return 0.0, 0.0


if __name__ == "__main__":
    model, budget = build()
    for cut in (1, 6):
        print(cut, what_if(model, budget, cut))

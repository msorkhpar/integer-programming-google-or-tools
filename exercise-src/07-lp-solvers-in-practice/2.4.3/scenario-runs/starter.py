from __future__ import annotations

from ortools.math_opt.python import mathopt


def build() -> tuple[mathopt.Model, dict[str, mathopt.LinearConstraint]]:
    """The depot overhaul LP. Given: you do not need to change it."""
    model = mathopt.Model(name="depots")
    a = model.add_variable(lb=0, ub=4, name="hours_A")
    b = model.add_variable(lb=0, ub=5, name="hours_B")
    c = model.add_variable(lb=0, ub=10, name="hours_C")
    rows = {
        "budget": model.add_linear_constraint(2 * a + 2 * b + c <= 20, name="budget"),
        "staff": model.add_linear_constraint(a + b + c <= 9, name="staff"),
        "service": model.add_linear_constraint(a >= 3, name="service"),
    }
    model.maximize(6 * a + 5 * b + 2 * c)
    return model, rows


def run_scenarios(model: mathopt.Model, rows: dict[str, mathopt.LinearConstraint],
                  scenarios: list[dict[str, float]]) -> list[float | None]:
    """Solve each scenario from the base data, on one incremental GLOP solver.

    A scenario maps row names to new upper bounds. Each scenario's objective is returned in order,
    or None when that scenario does not end OPTIMAL. The model is left as it was given.
    """
    # TODO: one IncrementalSolver for all scenarios; for each scenario set the bounds, solve,
    # read the status before the value, then put the bounds back.
    return [0.0 for _ in scenarios]


if __name__ == "__main__":
    model, rows = build()
    print(run_scenarios(model, rows, [{}, {"budget": 14}, {"staff": 12}, {"budget": 5}]))

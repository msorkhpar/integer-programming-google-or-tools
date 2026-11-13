from __future__ import annotations

from ortools.math_opt.python import mathopt


def keep_within(model: mathopt.Model, expr, best: float, is_maximize: bool,
                params: mathopt.ObjectiveParameters | None):
    """Add and return the row keeping `expr` within its allowed loss of `best`."""
    # TODO: the allowed loss, then a row whose direction follows the objective's sense.
    return None


if __name__ == "__main__":
    model = mathopt.Model()
    cost = model.add_variable(lb=-1e6, ub=1e6, name="cost")
    print(keep_within(model, cost, 1000, False, mathopt.ObjectiveParameters(objective_degradation_absolute_tolerance=5)))

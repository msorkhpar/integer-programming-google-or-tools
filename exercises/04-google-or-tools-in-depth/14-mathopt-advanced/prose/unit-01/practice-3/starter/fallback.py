from __future__ import annotations

from ortools.math_opt.python import mathopt


def solve_first(model: mathopt.Model, solvers: list[mathopt.SolverType]):
    """(the first solver that accepts the model, its result, {refusing solver name: its reason})."""
    reasons: dict[str, str] = {}
    # TODO: try each solver in order; record each refusal's real reason.
    return None, None, reasons


if __name__ == "__main__":
    model = mathopt.Model()
    z, y = model.add_binary_variable(name="z"), model.add_variable(lb=0, ub=10, name="y")
    model.add_indicator_constraint(indicator=z, implied_constraint=y <= 3)
    model.maximize(y + z)
    print(solve_first(model, [mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP]))

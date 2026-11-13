from __future__ import annotations

from typing import Callable

from ortools.math_opt.python import mathopt

TOLERANCE = 1e-6


def lp_value(model: mathopt.Model) -> float:
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


def compare(build_a: Callable, build_b: Callable, objectives: list, sense: str = "max") -> str:
    """Which formulation's LP bound is tighter on these objectives: "a", "b", "same" or "neither".

    `build_a(objective)` and `build_b(objective)` return the LP relaxation of each formulation with
    that objective set; `sense` is "max" or "min", the same for both.
    """
    # TODO: solve both relaxations for each objective and decide.
    return None


if __name__ == "__main__":
    def one_row(objective):
        model = mathopt.Model()
        u, v = model.add_variable(lb=0, ub=1), model.add_variable(lb=0, ub=1)
        model.add_linear_constraint(u + v <= 1)
        model.maximize(objective[0] * u + objective[1] * v)
        return model

    print(compare(one_row, one_row, [(1, 1)]))

from __future__ import annotations

from ortools.math_opt.python import mathopt


def hint_params(y: dict[str, mathopt.Variable], chosen: set[str], complete: bool) -> mathopt.ModelSolveParameters:
    """Model parameters holding one hint: last week's plan, complete or only its chosen routes."""
    # TODO: one SolutionHint in solution_hints.
    return mathopt.ModelSolveParameters()


def build(routes: dict[str, tuple[float, float]], vans: int) -> tuple[mathopt.Model, dict]:
    """routes: name -> (profit, vans needed)."""
    model = mathopt.Model(name="routes")
    y = {r: model.add_binary_variable(name=f"y_{r}") for r in routes}
    model.add_linear_constraint(sum(routes[r][1] * y[r] for r in routes) <= vans, name="vans")
    model.maximize(sum(routes[r][0] * y[r] for r in routes))
    return model, y


if __name__ == "__main__":
    model, y = build({"north": (40, 2), "south": (30, 1), "east": (25, 2)}, 3)
    print(hint_params(y, {"north", "south"}, complete=True).solution_hints)

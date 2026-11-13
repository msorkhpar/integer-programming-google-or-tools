from __future__ import annotations

from ortools.math_opt.python import mathopt


def objective_without(model: mathopt.Model, variables: list[mathopt.Variable], solver: mathopt.SolverType) -> float:
    """The optimum with every variable in `variables` held at 0; the model is left exactly as it was."""
    old = {v: v.upper_bound for v in variables}
    try:
        for v in variables:
            v.upper_bound = 0.0
        return mathopt.solve(model, solver).objective_value()
    finally:
        for v, bound in old.items():
            v.upper_bound = bound


def build(towers: dict[str, tuple[float, float, int]], budget: float):
    """towers: name -> (value per radio, cost per radio, most radios)."""
    model = mathopt.Model(name="towers")
    u = {k: model.add_integer_variable(lb=0, ub=towers[k][2], name=f"u_{k}") for k in towers}
    model.add_linear_constraint(sum(towers[k][1] * u[k] for k in towers) <= budget, name="budget")
    model.maximize(sum(towers[k][0] * u[k] for k in towers))
    return model, u


if __name__ == "__main__":
    model, u = build({"hill": (5, 2, 3), "mall": (4, 1, 2)}, 6)
    print(objective_without(model, [u["hill"]], mathopt.SolverType.HIGHS))

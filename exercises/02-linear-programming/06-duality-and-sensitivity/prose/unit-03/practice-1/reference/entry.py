from __future__ import annotations

from ortools.math_opt.python import mathopt


def entry_values(model: mathopt.Model, tol: float = 1e-9) -> dict[str, float]:
    """For each variable the optimal plan leaves at 0: the objective coefficient at which it starts to pay."""
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return {}
    out = {}
    for var in model.variables():
        if abs(result.variable_values(var)) <= tol:
            coefficient = model.objective.get_linear_coefficient(var)
            out[var.name] = coefficient - result.reduced_costs(var)
    return out


if __name__ == "__main__":
    model = mathopt.Model()
    roofs = model.add_variable(lb=0, name="roofs")
    paint = model.add_variable(lb=0, name="paint")
    model.add_linear_constraint(roofs + paint <= 100, name="budget")
    model.maximize(0.6 * roofs + 0.2 * paint)
    print(entry_values(model))

from __future__ import annotations

from ortools.math_opt.python import mathopt


def fix_plan(model: mathopt.Model, result: mathopt.SolveResult) -> None:
    """Fix every integer variable at its value in `result`, and make it continuous."""
    for v in model.variables():
        if v.integer:
            value = round(result.variable_values(v))
            v.integer = False
            v.lower_bound = value
            v.upper_bound = value


def price_directions(model: mathopt.Model, result: mathopt.SolveResult, row_name: str, step: float) -> dict:
    """The fixed-integer price of a <= row, and whether it forecasts the fixed plan's change for +step and -step."""
    fix_plan(model, result)
    row = next(r for r in model.linear_constraints() if r.name == row_name)
    base = mathopt.solve(model, mathopt.SolverType.GLOP)
    price, limit = base.dual_values(row), row.upper_bound
    answer = {"price": price}
    for label, change in (("up", step), ("down", -step)):
        row.upper_bound = limit + change                  # from the original limit each time
        moved = mathopt.solve(model, mathopt.SolverType.GLOP)
        answer[label] = (moved.termination.reason == mathopt.TerminationReason.OPTIMAL
                         and abs(moved.objective_value() - base.objective_value() - price * change) <= 1e-6)
    row.upper_bound = limit
    return answer


if __name__ == "__main__":
    m = mathopt.Model()
    north = m.add_binary_variable(name="north")
    overtime = m.add_variable(lb=0, ub=20, name="overtime")
    m.add_linear_constraint(40 * north + overtime <= 50, name="budget")
    m.maximize(60 * north + 0.5 * overtime)
    print(price_directions(m, mathopt.solve(m, mathopt.SolverType.HIGHS), "budget", 5))

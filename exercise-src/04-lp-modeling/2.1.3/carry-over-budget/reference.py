from __future__ import annotations

from ortools.math_opt.python import mathopt


def plan_spending(budgets: dict[int, float], work: dict[int, float], value: dict[int, float], max_carry: float):
    """Spend each year's budget, with carry-over into the next year. Returns (status, value, spend, carry)."""
    years = sorted(budgets)
    model = mathopt.Model(name="parks carry-over")
    x = {y: model.add_variable(lb=0, ub=work[y], name=f"x_{y}") for y in years}
    carry = {}
    for y in years:
        carry[y] = model.add_variable(lb=0, ub=max_carry * budgets[y], name=f"r_{y}")
    for i, y in enumerate(years):
        incoming = carry[years[i - 1]] if i else 0
        model.add_linear_constraint(x[y] + carry[y] <= budgets[y] + incoming, name=f"cash_{y}")
    model.maximize(sum(value[y] * x[y] for y in years))
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    status = result.termination.reason.name
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return status, None, None, None
    spend = {y: result.variable_values(x[y]) for y in years}
    return status, result.objective_value(), spend, {y: result.variable_values(carry[y]) for y in years}


if __name__ == "__main__":
    print(plan_spending({2030: 100, 2031: 100}, {2030: 60, 2031: 150}, {2030: 1.0, 2031: 0.9}, 0.5))

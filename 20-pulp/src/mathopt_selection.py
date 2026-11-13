"""Lesson 5.2.2: the inherited PuLP selection script, ported to MathOpt with the same names."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


def build(portfolio: Portfolio) -> tuple[mathopt.Model, dict[str, mathopt.Variable]]:
    model = mathopt.Model(name="selection")
    x = {p.project_id: model.add_binary_variable(name="x_" + p.project_id) for p in portfolio.projects}
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))

    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                <= portfolio.capital_budget, name="budget")
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name="must_" + p.project_id)
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name="parent_" + p.project_id)

    groups: dict[str, list[mathopt.Variable]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(x[p.project_id])
    for g, members in groups.items():
        model.add_linear_constraint(sum(members) <= 1, name="alt_" + g)
    return model, x


def solve_ported(portfolio: Portfolio, solver: mathopt.SolverType = mathopt.SolverType.HIGHS,
                 gap: float | None = None):
    """Return (termination reason, value, funded project ids, model), or a value of None with no plan."""
    model, x = build(portfolio)
    result = mathopt.solve(model, solver, params=mathopt.SolveParameters(relative_gap_tolerance=gap))
    reason = result.termination.reason
    if reason not in (mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE):
        return reason.name, None, [], model
    values = result.variable_values()
    return reason.name, result.objective_value(), [pid for pid, v in x.items() if values[v] > 0.5], model

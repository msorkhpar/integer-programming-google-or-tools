from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0, absolute_gap_tolerance=0.0)


@dataclass(frozen=True)
class Project:
    pid: str
    value: int
    cost: int
    must_do: bool = False


def build(projects: list[Project], budget: int) -> tuple[mathopt.Model, dict]:
    """Given: the one-budget selection with its must-dos."""
    model = mathopt.Model(name="selection")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    model.add_linear_constraint(sum(p.cost * x[p.pid] for p in projects) <= budget, name="budget")
    for p in projects:
        if p.must_do:
            model.add_linear_constraint(x[p.pid] == 1, name=f"must_{p.pid}")
    model.maximize(sum(p.value * x[p.pid] for p in projects))
    return model, x


def decision_costs(projects: list[Project], budget: int) -> dict[str, float | None]:
    """For each project, what the best plan loses when its decision is reversed; None if the rules refuse it."""
    model, x = build(projects, budget)
    base = mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT)
    best = base.objective_value()
    funded = {pid: base.variable_values(v) > 0.5 for pid, v in x.items()}
    costs: dict[str, float | None] = {}
    for p in projects:
        var = x[p.pid]
        low, high = var.lower_bound, var.upper_bound
        target = 0.0 if funded[p.pid] else 1.0
        var.lower_bound = var.upper_bound = target
        result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT)
        if result.termination.reason == mathopt.TerminationReason.OPTIMAL:
            costs[p.pid] = best - result.objective_value()
        else:
            costs[p.pid] = None
        var.lower_bound, var.upper_bound = low, high
    return costs


if __name__ == "__main__":
    print(decision_costs([Project("A", 60, 30), Project("B", 50, 20), Project("C", 40, 20)], 50))

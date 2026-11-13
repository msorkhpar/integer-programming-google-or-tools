from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    parent: str | None = None


def solve(projects: list[Project], budget: int, integer: bool) -> float:
    """The selection model's optimal value: the MILP with HiGHS, or its LP relaxation with GLOP."""
    model = mathopt.Model(name="selection")
    x = {p.pid: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.pid}") for p in projects}
    model.add_linear_constraint(sum(p.cost * x[p.pid] for p in projects) <= budget, name="budget")
    for p in projects:
        if p.parent:
            model.add_linear_constraint(x[p.pid] <= x[p.parent], name=f"parent_{p.pid}")
    model.maximize(sum(p.value * x[p.pid] for p in projects))
    solver = mathopt.SolverType.HIGHS if integer else mathopt.SolverType.GLOP
    return mathopt.solve(model, solver).objective_value()


def integrality_gap(projects: list[Project], budget: int) -> tuple[float, float, float]:
    """(LP bound, best plan's value, integrality gap as a share of the best plan's value)."""
    lp_bound = solve(projects, budget, integer=False)
    optimum = solve(projects, budget, integer=True)
    return lp_bound, optimum, (lp_bound - optimum) / abs(optimum)


if __name__ == "__main__":
    yards = [Project("A", 60, 66), Project("B", 50, 60), Project("C", 40, 36)]
    print(integrality_gap(yards, 100))
    linked = [Project("P", 50, 40), Project("Q", 40, 64, parent="P"), Project("R", 30, 30)]
    print(integrality_gap(linked, 100))

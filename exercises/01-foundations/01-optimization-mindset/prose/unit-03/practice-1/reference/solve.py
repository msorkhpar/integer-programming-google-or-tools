from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    must_do: bool = False


def solve_plan(projects: list[Project], budget: int) -> tuple[str, float | None, frozenset[str] | None]:
    """Build the selection model, solve it with HiGHS, and read the answer status first."""
    model = mathopt.Model(name="selection")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    model.add_linear_constraint(sum(p.cost * x[p.pid] for p in projects) <= budget, name="budget")
    for p in projects:
        if p.must_do:
            model.add_linear_constraint(x[p.pid] == 1, name=f"must_{p.pid}")
    model.maximize(sum(p.value * x[p.pid] for p in projects))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    status = result.termination.reason.name
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return status, None, None
    plan = frozenset(pid for pid, var in x.items() if result.variable_values(var) > 0.5)
    return status, result.objective_value(), plan


if __name__ == "__main__":
    demo = [Project("A", 50, 80, must_do=True), Project("B", 30, 40), Project("C", 20, 35)]
    print(solve_plan(demo, 90))
    print(solve_plan(demo, 40))

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    must_do: bool = False
    parent: str | None = None
    group: str | None = None


def add_rules(model: mathopt.Model, x: dict, projects: list[Project]) -> None:
    """Add the must-do, parent-child and alternative rules as linear constraints."""
    # TODO: one linear constraint per rule, written with the variables in x.
    return None


def build_model(projects: list[Project], budget: int) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="selection")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    model.add_linear_constraint(sum(p.cost * x[p.pid] for p in projects) <= budget, name="budget")
    add_rules(model, x, projects)
    model.maximize(sum(p.value * x[p.pid] for p in projects))
    return model, x


def solve(projects: list[Project], budget: int) -> tuple[float, frozenset[str]]:
    model, x = build_model(projects, budget)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.objective_value(), frozenset(pid for pid, v in x.items() if result.variable_values(v) > 0.5)


if __name__ == "__main__":
    demo = [Project("A", 50, 80, must_do=True), Project("B", 30, 40), Project("C", 20, 35, parent="B")]
    print(solve(demo, 90))

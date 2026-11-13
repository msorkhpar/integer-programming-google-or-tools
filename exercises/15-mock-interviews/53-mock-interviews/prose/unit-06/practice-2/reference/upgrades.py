from __future__ import annotations

from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int            # $k
    crew: int            # crew-weeks
    region: str
    value: int = 0


@dataclass(frozen=True)
class Limits:
    budget: int
    crew: int
    region_cap: dict[str, int]
    conflicts: list[tuple[str, str]] = field(default_factory=list)   # not both
    needs: list[tuple[str, str]] = field(default_factory=list)       # (a, b): a only if b


def add_rules(model: mathopt.Model, x: dict, projects: list[Project], limits: Limits) -> None:
    """Budget, crew-weeks, a cap per region, conflicting pairs and needs."""
    model.add_linear_constraint(sum(p.cost * x[p.pid] for p in projects) <= limits.budget, name="budget")
    model.add_linear_constraint(sum(p.crew * x[p.pid] for p in projects) <= limits.crew, name="crews")
    for region, cap in limits.region_cap.items():
        members = [x[p.pid] for p in projects if p.region == region]
        if members:
            model.add_linear_constraint(sum(members) <= cap, name=f"region_{region}")
    for a, b in limits.conflicts:
        model.add_linear_constraint(x[a] + x[b] <= 1, name=f"conflict_{a}_{b}")
    for a, b in limits.needs:
        model.add_linear_constraint(x[a] - x[b] <= 0, name=f"needs_{a}_{b}")


def build(projects: list[Project], limits: Limits) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="tower-upgrades")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    add_rules(model, x, projects, limits)
    model.maximize(sum(p.value * x[p.pid] for p in projects))
    return model, x


if __name__ == "__main__":
    model, x = build([Project("A", 40, 3, "N", 10), Project("B", 30, 2, "N", 8)], Limits(60, 4, {"N": 1}))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    print(result.termination.reason.name, result.objective_value())

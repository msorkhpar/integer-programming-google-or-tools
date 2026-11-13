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
    # TODO: the rows of your formulation.
    return None


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

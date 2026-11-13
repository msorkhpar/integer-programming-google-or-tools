from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    mandated: bool = False


def best_value(projects: list[Project], budget: int, enforced: set[str]) -> float:
    """The best total value within the budget, with every project in `enforced` funded."""
    model = mathopt.Model(name="parks")
    pick = {p.pid: model.add_binary_variable(name=f"pick_{p.pid}") for p in projects}
    model.add_linear_constraint(sum(p.cost * pick[p.pid] for p in projects) <= budget, name="budget")
    for pid in enforced:
        pick[pid].lower_bound = 1.0
    model.maximize(sum(p.value * pick[p.pid] for p in projects))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.objective_value()


def mandate_costs(projects: list[Project], budget: int) -> dict[str, float]:
    """Each mandated project's cost, and the cost of all mandates together under "all"."""
    mandated = {p.pid for p in projects if p.mandated}
    with_all = best_value(projects, budget, mandated)
    costs = {pid: best_value(projects, budget, mandated - {pid}) - with_all for pid in sorted(mandated)}
    costs["all"] = best_value(projects, budget, set()) - with_all
    return costs


if __name__ == "__main__":
    projects = [Project("PLAY", 4, 5, mandated=True), Project("POOL", 6, 9), Project("PATH", 3, 4)]
    print(mandate_costs(projects, 9))

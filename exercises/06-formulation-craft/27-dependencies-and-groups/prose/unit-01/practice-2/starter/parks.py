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
    # TODO: build the selection model, solve it and return its objective value.
    return 0.0


def mandate_costs(projects: list[Project], budget: int) -> dict[str, float]:
    """Each mandated project's cost, and the cost of all mandates together under "all"."""
    # TODO: compare best values with and without each mandate. Every cost below is a placeholder.
    costs = {p.pid: -1.0 for p in projects if p.mandated}
    costs["all"] = -1.0
    return costs


if __name__ == "__main__":
    projects = [Project("PLAY", 4, 5, mandated=True), Project("POOL", 6, 9), Project("PATH", 3, 4)]
    print(mandate_costs(projects, 9))

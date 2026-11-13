from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    must_do: bool = False
    parent: str | None = None
    group: str | None = None


def allowed(plan: set[str], projects: list[Project], budget: int) -> bool:
    """True if the plan keeps the budget, must-do, parent and alternative rows."""
    if sum(p.cost for p in projects if p.pid in plan) > budget:
        return False
    for p in projects:
        if p.must_do and p.pid not in plan:
            return False
        if p.parent and p.pid in plan and p.parent not in plan:
            return False
    groups = [p.group for p in projects if p.group and p.pid in plan]
    return len(groups) == len(set(groups))


def count_allowed(projects: list[Project], budget: int) -> int:
    """How many of the 2^n plans keep every rule, checking each one."""
    ids = [p.pid for p in projects]
    return sum(allowed(set(plan), projects, budget)
               for k in range(len(ids) + 1) for plan in combinations(ids, k))


if __name__ == "__main__":
    bays = [Project("M", 40, must_do=True), Project("A", 30), Project("B", 20, group="G"), Project("C", 25, group="G")]
    print(count_allowed(bays, 100))

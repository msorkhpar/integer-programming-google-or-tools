from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    must_do: bool = False
    parent: str | None = None
    group: str | None = None


def round_down_and_fill(shares: dict[str, float], projects: list[Project], budget: int) -> set[str]:
    """Keep the projects the LP funded whole, then add the rest best value per dollar while they fit the rules."""
    plan = {pid for pid, share in shares.items() if share > 1 - 1e-6}
    spent = sum(p.cost for p in projects if p.pid in plan)
    for p in sorted(projects, key=lambda p: p.value / p.cost, reverse=True):
        if p.pid in plan or spent + p.cost > budget:
            continue
        if p.parent and p.parent not in plan:
            continue
        if p.group and any(q.group == p.group and q.pid in plan for q in projects):
            continue
        plan.add(p.pid)
        spent += p.cost
    return plan


if __name__ == "__main__":
    pipes = [Project("A", 50, 60, must_do=True), Project("B", 40, 52), Project("H", 30, 24), Project("F", 10, 9)]
    print(round_down_and_fill({"A": 1.0, "B": 0.25, "H": 0.0, "F": 0.0}, pipes, 100))

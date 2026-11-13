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


def broken_rows(plan: set[str], projects: list[Project], budget: int) -> set[str]:
    """The labels of the rows a 0/1 plan breaks: budget, must_<pid>, parent_<pid>, alt_<group>."""
    broken = set()
    if sum(p.cost for p in projects if p.pid in plan) > budget:
        broken.add("budget")
    funded_in_group: dict[str, int] = {}
    for p in projects:
        if p.must_do and p.pid not in plan:
            broken.add(f"must_{p.pid}")
        if p.parent and p.pid in plan and p.parent not in plan:
            broken.add(f"parent_{p.pid}")
        if p.group and p.pid in plan:
            funded_in_group[p.group] = funded_in_group.get(p.group, 0) + 1
    broken |= {f"alt_{g}" for g, n in funded_in_group.items() if n > 1}
    return broken


if __name__ == "__main__":
    mains = [Project("M1", 40, 55, must_do=True), Project("M2", 30, 42), Project("M3", 30, 36, parent="M2"),
             Project("M4", 20, 26, group="G1"), Project("M5", 15, 24, group="G1")]
    print(broken_rows({"M1", "M2", "M3", "M4", "M5"}, mains, 100))
    print(broken_rows({"M2", "M3"}, mains, 100))

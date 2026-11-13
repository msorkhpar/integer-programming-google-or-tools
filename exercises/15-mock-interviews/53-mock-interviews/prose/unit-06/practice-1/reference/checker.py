from __future__ import annotations

from dataclasses import dataclass, field


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


def broken_rules(plan: set[str], projects: list[Project], limits: Limits) -> list[str]:
    """Every rule the plan breaks, read from the data alone, as sorted labels."""
    chosen = [p for p in projects if p.pid in plan]
    broken = []
    if sum(p.cost for p in chosen) > limits.budget:
        broken.append("budget")
    if sum(p.crew for p in chosen) > limits.crew:
        broken.append("crews")
    for region, cap in limits.region_cap.items():
        if sum(1 for p in chosen if p.region == region) > cap:
            broken.append(f"region_{region}")
    for a, b in limits.conflicts:
        if a in plan and b in plan:
            broken.append(f"conflict_{a}_{b}")
    for a, b in limits.needs:
        if a in plan and b not in plan:
            broken.append(f"needs_{a}_{b}")
    return sorted(broken)


if __name__ == "__main__":
    projects = [Project("A", 40, 3, "N"), Project("B", 30, 2, "N")]
    print(broken_rules({"A", "B"}, projects, Limits(60, 4, {"N": 1})))

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
    # TODO: check each rule against the plan, using only the data.
    return ["unchecked"]


if __name__ == "__main__":
    projects = [Project("A", 40, 3, "N"), Project("B", 30, 2, "N")]
    print(broken_rules({"A", "B"}, projects, Limits(60, 4, {"N": 1})))

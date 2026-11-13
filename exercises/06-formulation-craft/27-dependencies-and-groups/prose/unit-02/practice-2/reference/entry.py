from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    cost: int
    needs: tuple[str, ...] = ()


def prerequisites(projects: dict[str, Project], pid: str, seen: set[str] | None = None) -> set[str]:
    """Every project `pid` needs, directly or indirectly, each once."""
    seen = set() if seen is None else seen
    for need in projects[pid].needs:
        if need not in seen:
            seen |= {need} | prerequisites(projects, need, seen | {need})
    return seen


def entry_cost(projects: dict[str, Project], pid: str) -> int:
    """The cost of `pid` and of every project it needs, directly or indirectly, each counted once."""
    return projects[pid].cost + sum(projects[n].cost for n in prerequisites(projects, pid))


def implied_required(projects: dict[str, Project], required: set[str]) -> set[str]:
    """Projects outside `required` that a required project needs, directly or indirectly."""
    return set().union(*(prerequisites(projects, pid) for pid in required)) - required


if __name__ == "__main__":
    projects = {"MAIN": Project(500), "PUMP": Project(200, ("MAIN",))}
    print(entry_cost(projects, "PUMP"), implied_required(projects, {"PUMP"}))

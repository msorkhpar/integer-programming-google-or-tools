from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    cost: int
    needs: tuple[str, ...] = ()


def entry_cost(projects: dict[str, Project], pid: str) -> int:
    """The cost of `pid` and of every project it needs, directly or indirectly, each counted once."""
    # TODO: walk the needs.
    return 0


def implied_required(projects: dict[str, Project], required: set[str]) -> set[str]:
    """Projects outside `required` that a required project needs, directly or indirectly."""
    # TODO: walk the needs of every required project.
    return {"?"}


if __name__ == "__main__":
    projects = {"MAIN": Project(500), "PUMP": Project(200, ("MAIN",))}
    print(entry_cost(projects, "PUMP"), implied_required(projects, {"PUMP"}))

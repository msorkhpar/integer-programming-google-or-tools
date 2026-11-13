from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    pid: str
    program: str
    earliest: int
    latest: int
    duration: int                  # years of work
    must_do: bool = False
    alt_group: str | None = None
    parent: str | None = None
    lag: int = 0


def rows_for(pid: str, projects: list[Project], years: list[int]) -> set[str]:
    """The names of every row in which one of project `pid`'s start variables appears."""
    # TODO: go through the model's rows one kind at a time. The empty set is a placeholder.
    return set()


if __name__ == "__main__":
    projects = [Project("S1", "substations", 2027, 2028, 2), Project("S2", "substations", 2029, 2029, 1, parent="S1", lag=1)]
    print(sorted(rows_for("S1", projects, [2027, 2028, 2029])))

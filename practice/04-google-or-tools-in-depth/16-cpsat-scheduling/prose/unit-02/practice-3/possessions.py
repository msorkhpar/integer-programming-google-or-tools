from __future__ import annotations

from ortools.sat.python import cp_model


def possession_plan(jobs: dict[str, tuple[str, int]], possessions: dict[str, list[tuple[int, int]]]) -> dict[str, int]:
    """Start day of each job, inside one possession of its line, so the last ends as early as possible."""
    # TODO: a start per job whose domain keeps the job inside a possession, an interval per job,
    # a NoOverlap per line, and minimize the latest end. Every start below is a placeholder.
    return {name: -1 for name in jobs}


if __name__ == "__main__":
    print(possession_plan({"rails": ("north", 3), "points": ("north", 2), "drain": ("south", 4)},
                          {"north": [(0, 3), (8, 12)], "south": [(2, 9)]}))

from __future__ import annotations

from ortools.sat.python import cp_model


def paving_plan(jobs: dict[str, tuple[int, int]], gangs: int, horizon: int) -> dict[str, int]:
    """Start day of each job, so the last ends as early as possible; {} if no plan exists."""
    # TODO: an interval per job, one cumulative constraint over the pool, minimize the latest end,
    # and check the status before reading the starts. Every start below is a placeholder.
    return {name: -1 for name in jobs}


if __name__ == "__main__":
    print(paving_plan({"elm": (3, 2), "oak": (2, 1), "ash": (4, 1)}, 3, 20))

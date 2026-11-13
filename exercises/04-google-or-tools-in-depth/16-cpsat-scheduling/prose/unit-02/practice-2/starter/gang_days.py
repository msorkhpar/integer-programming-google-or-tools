from __future__ import annotations

from ortools.sat.python import cp_model


def holiday_plan(jobs: dict[str, tuple[int, int]], available: list[int]) -> dict[str, int]:
    """Start day of each job under a pool that changes by day, so the last ends as early as possible."""
    # TODO: one interval per job; the cumulative at the peak, with fixed intervals holding the
    # missing gangs on each run of days below the peak. Every start below is a placeholder.
    return {name: -1 for name in jobs}


if __name__ == "__main__":
    print(holiday_plan({"elm": (3, 2), "oak": (2, 1), "ash": (4, 1)}, [3, 3, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3]))

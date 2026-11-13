from __future__ import annotations

from ortools.sat.python import cp_model


def shortest_schedule(jobs: dict[str, int], booked: list[tuple[int, int]], horizon: int) -> dict[str, int]:
    """Start day of each job on one rig, so the last job ends as early as possible."""
    # TODO: one interval per job, one fixed interval per booking, NoOverlap over all of them,
    # and minimize the latest end. Every start below is a placeholder.
    return {name: -1 for name in jobs}


if __name__ == "__main__":
    print(shortest_schedule({"S1": 3, "S2": 2, "S3": 4}, [(4, 5)], 20))

from __future__ import annotations

from ortools.sat.python import cp_model


def split_work(jobs: dict[str, int], teams: list[str], away: dict[str, list[tuple[int, int]]],
               horizon: int) -> dict[str, tuple[str, int]]:
    """(team, start day) for each job, so the last job ends as early as possible."""
    # TODO: a start per job, a Boolean and an optional interval per job and team, exactly one team
    # per job, a NoOverlap per team with its absences, and minimize the latest end.
    # Every pair below is a placeholder.
    return {j: ("nobody", -1) for j in jobs}


if __name__ == "__main__":
    print(split_work({"main_st": 3, "mill_rd": 2, "dam": 4}, ["red", "blue"], {"blue": [(0, 1)]}, 20))

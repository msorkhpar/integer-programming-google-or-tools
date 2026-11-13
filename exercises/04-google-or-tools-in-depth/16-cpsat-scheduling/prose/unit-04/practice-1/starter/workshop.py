from __future__ import annotations

from ortools.sat.python import cp_model


def least_penalty(jobs: dict[str, tuple[int, int, int, int]], mechanics: int,
                  horizon: int) -> tuple[int, dict[str, int]]:
    """(least total penalty, start day of each job) under a pool of mechanics."""
    # TODO: an interval per job, the cumulative over the mechanics, a lateness variable per job set
    # to max(0, end - due), and minimize the weighted lateness. Placeholders below.
    return -1, {name: -1 for name in jobs}


if __name__ == "__main__":
    print(least_penalty({"lathe": (3, 1, 3, 5), "press": (2, 2, 4, 9), "pump": (2, 1, 2, 1)}, 2, 20))

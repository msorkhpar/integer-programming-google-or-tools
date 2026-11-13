from __future__ import annotations

import numpy as np


def spend_matrix(projects: list[tuple[str, int, list[float]]], years: list[int]) -> np.ndarray:
    """A[r, j]: what project j spends in years[r]."""
    # TODO: for each project j and each year of work k, find the row of year start + k, if any.
    return np.zeros((len(years), len(projects)))


def needs_matrix(projects: list[tuple[str, int, list[float]]], parent_of: dict[str, str]) -> np.ndarray:
    """One row per child: +1 in the child's column, -1 in its parent's."""
    # TODO: map each project id to its column, then fill one row per child.
    return np.zeros((len(parent_of), len(projects)))


if __name__ == "__main__":
    projects = [("pump", 2030, [400.0]), ("main", 2031, [250.0, 250.0])]
    print(spend_matrix(projects, [2030, 2031, 2032]))
    print(needs_matrix(projects, {"main": "pump"}))

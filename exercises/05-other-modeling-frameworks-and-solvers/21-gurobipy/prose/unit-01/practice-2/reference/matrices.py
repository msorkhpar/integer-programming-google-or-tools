from __future__ import annotations

import numpy as np


def spend_matrix(projects: list[tuple[str, int, list[float]]], years: list[int]) -> np.ndarray:
    """A[r, j]: what project j spends in years[r]."""
    row = {y: r for r, y in enumerate(years)}
    A = np.zeros((len(years), len(projects)))
    for j, (_, start, profile) in enumerate(projects):
        for k, amount in enumerate(profile):
            if start + k in row:
                A[row[start + k], j] += amount
    return A


def needs_matrix(projects: list[tuple[str, int, list[float]]], parent_of: dict[str, str]) -> np.ndarray:
    """One row per child: +1 in the child's column, -1 in its parent's."""
    col = {pid: j for j, (pid, _, _) in enumerate(projects)}
    N = np.zeros((len(parent_of), len(projects)))
    for r, (child, parent) in enumerate(parent_of.items()):
        N[r, col[child]] = 1.0
        N[r, col[parent]] = -1.0
    return N


if __name__ == "__main__":
    projects = [("pump", 2030, [400.0]), ("main", 2031, [250.0, 250.0])]
    print(spend_matrix(projects, [2030, 2031, 2032]))
    print(needs_matrix(projects, {"main": "pump"}))

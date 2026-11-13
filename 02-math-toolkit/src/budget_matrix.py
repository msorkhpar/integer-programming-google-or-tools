"""GridCap's yearly budget matrix: one row per year, one column per project, A @ x <= b.

Each funded project starts in its earliest start year, so its cost profile fixes what it spends in
each year. (Section 6 lets the start year move.)
"""

import numpy as np

from gridcap import Portfolio, generate


def spend_matrix(portfolio: Portfolio) -> tuple[np.ndarray, np.ndarray]:
    """A[r, j]: what project j spends in year r if it starts as early as it can. b[r]: that year's budget."""
    A = np.zeros((len(portfolio.years), len(portfolio.projects)), dtype=int)
    for j, p in enumerate(portfolio.projects):
        for year, amount in p.spend(p.earliest_start).items():
            A[portfolio.years.index(year), j] = amount
    b = np.array([portfolio.budget[y] for y in portfolio.years])
    return A, b


tiny = generate("tiny")
A, b = spend_matrix(tiny)

if __name__ == "__main__":
    print("      ", " ".join(f"{pid:>5}" for pid in tiny.project_ids), "|      b")
    for year, row, limit in zip(tiny.years, A, b):
        print(year, "  ", " ".join(f"{v:>5}" for v in row), f"| {limit:>6}")
    x = np.array([1, 1, 0, 0, 1, 1, 0, 0])
    print()
    print("A @ x      =", A @ x)
    print("b          =", b)
    print("A @ x <= b =", A @ x <= b)
    print("slack b - A @ x =", b - A @ x)
    print("feasible:", bool(np.all(A @ x <= b)))
    broken = np.flatnonzero(A @ x > b)                # the positions where the mask is True
    print("broken rows:", broken)
    print("over budget in:", [tiny.years[r] for r in broken])

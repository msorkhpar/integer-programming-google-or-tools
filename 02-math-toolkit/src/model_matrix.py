"""GridCap's model matrix as triplets (row, column, value): only the nonzero entries.

Rows: one budget per year, one regional budget per (region, year), one row per parent rule
(x_child - x_parent <= 0) and one per alternative group (sum <= 1). Columns: one per project, which
starts in its earliest start year, as in lesson 1.2.1. Must-do projects are variable bounds, not rows.
"""

from __future__ import annotations

import numpy as np
from scipy import sparse

from gridcap import REGIONS, Portfolio


def triplets(portfolio: Portfolio) -> tuple[list[int], list[int], list[int], list[str], list[int]]:
    """The nonzeros of A as three parallel lists, plus each row's name and right-hand side."""
    col = {p.project_id: j for j, p in enumerate(portfolio.projects)}
    rows: list[int] = []
    cols: list[int] = []
    vals: list[int] = []
    names: list[str] = []
    rhs: list[int] = []

    def add_row(name: str, entries: list[tuple[int, int]], limit: int) -> None:
        for j, a in entries:
            rows.append(len(names))
            cols.append(j)
            vals.append(a)
        names.append(name)
        rhs.append(limit)

    spend = {p.project_id: p.spend(p.earliest_start) for p in portfolio.projects}
    for y in portfolio.years:
        add_row(f"budget_{y}", [(col[p.project_id], spend[p.project_id][y])
                                for p in portfolio.projects if y in spend[p.project_id]], portfolio.budget[y])
    for region in REGIONS:
        for y in portfolio.years:
            add_row(f"region_{region}_{y}", [(col[p.project_id], spend[p.project_id][y])
                                             for p in portfolio.projects
                                             if p.region == region and y in spend[p.project_id]],
                    portfolio.region_budget[region, y])
    for p in portfolio.projects:
        if p.parent:
            add_row(f"parent_{p.project_id}", [(col[p.project_id], 1), (col[p.parent], -1)], 0)
    groups: dict[str, list[int]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(col[p.project_id])
    for g in sorted(groups):
        add_row(f"alt_{g}", [(j, 1) for j in groups[g]], 1)
    return rows, cols, vals, names, rhs


def csr(portfolio: Portfolio) -> tuple[sparse.csr_array, np.ndarray, list[str]]:
    rows, cols, vals, names, rhs = triplets(portfolio)
    A = sparse.coo_array((vals, (rows, cols)), shape=(len(names), len(portfolio.projects))).tocsr()
    return A, np.array(rhs), names


def stored_bytes(A: sparse.csr_array) -> int:
    """What a CSR matrix keeps in memory: its three arrays."""
    return A.data.nbytes + A.indices.nbytes + A.indptr.nbytes

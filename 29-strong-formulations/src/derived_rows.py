"""Bounds and valid rows derived from the model's own rows: fixings, conflicts and clique rows.

Every function here reads GridCap's data and the rules of `strong_model.build(..., crews=True)`, and
returns facts that every whole plan obeys. None of them solves anything.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

from gridcap import PROGRAMS, Portfolio
from strong_model import active

Start = tuple[str, int]                     # (project, start year): one x variable


@dataclass(frozen=True)
class CapacityRow:
    name: str
    use: dict[Start, int]                    # how much of the row each start uses
    capacity: int


def capacity_rows(portfolio: Portfolio, crews: bool = True) -> list[CapacityRow]:
    """The budget row of every year and, with `crews`, the crew row of every program and year."""
    rows = []
    for year in portfolio.years:
        use = {(p.project_id, t): p.spend(t)[year] for p in portfolio.projects for t in p.starts()
               if year in p.spend(t)}
        rows.append(CapacityRow(f"budget_{year}", use, portfolio.budget[year]))
    for g in PROGRAMS if crews else ():
        for year in portfolio.years:
            use = {(p.project_id, t): p.crew_months for p in portfolio.projects if p.program == g
                   for t in p.starts() if active(p, t, year)}
            rows.append(CapacityRow(f"crews_{g}_{year}", use, portfolio.crews[g, year]))
    return rows


def room(portfolio: Portfolio, row: CapacityRow, fixed: dict[Start, str] | None = None) -> int:
    """What the row leaves for discretionary work: capacity less the least the must-dos can use of it.

    A must-do starts in one of its open years, so it uses at least the smallest of those starts'
    uses (0 if one of them does not touch this row). Starts already fixed at 0 are not open.
    """
    return row.capacity - sum(must_floor(portfolio, row, p.project_id, fixed)
                              for p in portfolio.projects if p.must_do)


def must_floor(portfolio: Portfolio, row: CapacityRow, pid: str, fixed: dict[Start, str] | None = None) -> int:
    """The least a must-do uses of the row, over its open starts; 0 for any other project."""
    p = portfolio.project(pid)
    if not p.must_do:
        return 0
    return min(row.use.get((pid, t), 0) for t in p.starts() if (pid, t) not in (fixed or {}))


def fixable(portfolio: Portfolio, crews: bool = True) -> dict[Start, tuple[int, str]]:
    """Starts no whole plan can use: alone they need more of some row than the row leaves them.

    Fixing a must-do's start raises what it must use elsewhere, which can fix more starts, so the
    pass repeats until nothing changes. Returns start -> (round, row that fixed it).
    """
    fixed: dict[Start, tuple[int, str]] = {}
    rows = capacity_rows(portfolio, crews)
    rounds = 0
    while True:
        rounds += 1
        found = {}
        for row in rows:
            left = room(portfolio, row, fixed)
            for (pid, t), a in row.use.items():
                if (pid, t) in fixed or (pid, t) in found:
                    continue
                # A must-do's own floor is already taken out of `left`: give it back before comparing.
                if a > left + must_floor(portfolio, row, pid, fixed):
                    found[pid, t] = (rounds, row.name)
        if not found:
            return fixed
        fixed.update(found)


def conflicts(portfolio: Portfolio, fixed: dict, crews: bool = True) -> set[frozenset[Start]]:
    """Pairs of starts that no whole plan uses together (see `conflict_reasons`)."""
    return set(conflict_reasons(portfolio, fixed, crews))


def conflict_reasons(portfolio: Portfolio, fixed: dict, crews: bool = True) -> dict[frozenset[Start], str]:
    """Pairs of starts that no whole plan uses together, each with the first reason found.

    Two starts of one project (a project starts once), starts of two projects in one alternative
    group, and two starts that together need more of a capacity row than it leaves.
    """
    starts = [(p.project_id, t) for p in portfolio.projects for t in p.starts() if (p.project_id, t) not in fixed]
    group = {p.project_id: p.alt_group for p in portfolio.projects}
    reasons: dict[frozenset[Start], str] = {}
    for u, v in itertools.combinations(starts, 2):
        if u[0] == v[0]:
            reasons[frozenset((u, v))] = f"once_{u[0]}"
        elif group[u[0]] is not None and group[u[0]] == group[v[0]]:
            reasons[frozenset((u, v))] = f"alt_{group[u[0]]}"
    for row in capacity_rows(portfolio, crews):
        left = room(portfolio, row, fixed)
        users = [s for s in row.use if s not in fixed]
        for u, v in itertools.combinations(users, 2):
            if u[0] == v[0]:
                continue
            extra = must_floor(portfolio, row, u[0], fixed) + must_floor(portfolio, row, v[0], fixed)
            if row.use[u] + row.use[v] > left + extra:
                reasons.setdefault(frozenset((u, v)), row.name)
    return reasons


def cliques(pairs: set[frozenset[Start]]) -> list[list[Start]]:
    """Cover every conflict with cliques: sets of starts that conflict two by two, grown greedily.

    Each edge not yet covered starts a clique, which takes every further start that conflicts with
    all of its members (in sorted order, so the result is the same every run).
    """
    near: dict[Start, set[Start]] = {}
    for pair in pairs:
        u, v = sorted(pair)
        near.setdefault(u, set()).add(v)
        near.setdefault(v, set()).add(u)
    covered: set[frozenset[Start]] = set()
    found = []
    for pair in sorted(pairs, key=sorted):
        if pair in covered:
            continue
        clique = sorted(pair)
        for w in sorted(set.intersection(*(near[c] for c in clique))):
            if all(w in near[c] for c in clique):
                clique.append(w)
        clique.sort()
        covered |= {frozenset(e) for e in itertools.combinations(clique, 2)}
        found.append(clique)
    return found


def already_a_row(clique: list[Start], portfolio: Portfolio) -> bool:
    """Is the clique inside one project's starts or one alternative group's (a row the model has)?"""
    projects = {pid for pid, _ in clique}
    groups = {portfolio.project(pid).alt_group for pid in projects}
    return len(projects) == 1 or (len(groups) == 1 and None not in groups)

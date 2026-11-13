"""The planners' business rules, one function per rule, each adding rows with the names it owns.

Every rule reads the request and the start variables through `built` and adds its rows with
`built.add(name, row)`. A new rule is a new function added to RULES; `build` never changes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ortools.math_opt.python import mathopt

if TYPE_CHECKING:
    from .model import Built


def once_or_must(built: Built) -> None:
    """(once_i) a project starts at most once; (must_i) a must-do starts exactly once."""
    for p in built.request.projects:
        if p.must_do:
            built.add(f"must_{p.project_id}", built.started(p.project_id) == 1)
        else:
            built.add(f"once_{p.project_id}", built.started(p.project_id) <= 1)


def alternatives(built: Built) -> None:
    """(alt_g) at most one project of an alternative group is funded."""
    for group, members in built.request.groups("alt_group").items():
        built.add(f"alt_{group}", mathopt.fast_sum(built.started(m) for m in members) <= 1)


def bundles(built: Built) -> None:
    """(bundle_{b,j}) each member of a bundle is funded exactly when its first member is."""
    for members in built.request.groups("bundle").values():
        first = members[0]
        for j in members[1:]:
            built.add(f"bundle_{first}_{j}", built.started(j) - built.started(first) == 0)


def parents(built: Built) -> None:
    """(after_{c,t}) a child started by year t needs its parent started by year t - lag."""
    request = built.request
    for c in request.projects:
        if c.parent is None:
            continue
        parent = request.project(c.parent)
        for t in request.starts(c):
            built.add(f"after_{c.project_id}_{t}",
                      built.started_by(c.project_id, t) - built.started_by(parent.project_id, t - c.parent_lag)
                      <= 0)


def budgets(built: Built) -> None:
    """(budget_y) each year's spend, with costs spread over the years of work, within its budget."""
    for y, spend in built.spend_by_year().items():
        built.add(f"budget_{y}", spend <= built.request.budget[y])


def risk_floor(built: Built) -> None:
    """(risk_floor) the plan removes at least the floor the planners set, when they set one."""
    if built.request.risk_floor is not None:
        built.add("risk_floor", built.risk >= built.request.risk_floor)


def overrides(built: Built) -> None:
    """(in_i) (out_i) (fix_{i,t}) a scenario's overrides, as named rows the diagnostics can name."""
    request = built.request
    for pid in request.force_in:
        built.add(f"in_{pid}", built.started(pid) == 1)
    for pid in request.force_out:
        built.add(f"out_{pid}", built.started(pid) == 0)
    for pid, year in sorted(request.fix_start.items()):
        built.add(f"fix_{pid}_{year}", built.started_by(pid, year) - built.started_by(pid, year - 1) == 1)


RULES = (once_or_must, alternatives, bundles, parents, budgets, risk_floor, overrides)

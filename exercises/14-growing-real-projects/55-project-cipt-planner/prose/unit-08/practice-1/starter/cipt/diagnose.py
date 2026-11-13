"""Why a request has no plan, and why a project was left out of one.

Both answers name rows, because every row has the name its rule gave it (lesson 14.2.3). A
deletion filter (lesson 9.1.3) relaxes one row at a time and keeps it relaxed while the model stays
infeasible; the rows it cannot relax form an irreducible conflict: drop any one of them and a plan
exists. Forcing a deferred project in (lesson 9.3.2) prices the decision, or, when forcing it in is
infeasible, finds the rows that block it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .data import Request
from .model import Built, build
from .solve import run_highs, solve_built


@dataclass(frozen=True)
class Conflict:
    rows: list[str]
    message: str


@dataclass(frozen=True)
class Deferral:
    project: str
    npv_cost: float                 # $k of NPV the plan gives up to fund the project
    displaced: tuple[str, ...]      # funded in the plan, dropped when the project is forced in
    conflict: Conflict | None       # the rows that make forcing it in impossible


def feasible(built: Built) -> bool:
    return run_highs(built.model).termination.reason.name != "INFEASIBLE"


def deletion_filter(built: Built, keep: tuple[str, ...] = ()) -> list[str]:
    """An irreducible set of rows that cannot all hold; rows in `keep` are never relaxed."""
    for name in sorted(built.rows):
        if name in keep:
            continue
        row = built.rows[name]
        bounds = (row.lower_bound, row.upper_bound)
        row.lower_bound, row.upper_bound = -math.inf, math.inf
        if feasible(built):
            row.lower_bound, row.upper_bound = bounds          # needed for the clash: restore it
    return sorted(n for n, r in built.rows.items() if (r.lower_bound, r.upper_bound) != (-math.inf, math.inf))


def describe(request: Request, name: str) -> str:
    """One row, in the planners' words."""
    kind, _, rest = name.partition("_")
    if kind == "budget":
        return f"spend in {rest} within ${request.budget[int(rest)]:,}k"
    if kind == "must":
        return f"{rest} is a must-do"
    if kind == "force":
        return f"{rest} is forced in"
    if kind == "alt":
        return f"at most one of {', '.join(request.groups('alt_group')[rest])}"
    if kind == "bundle":
        return f"{' and '.join(rest.split('_'))} are funded together or not at all"
    if kind == "after":
        child, year = rest.split("_")
        c = request.project(child)
        return f"{child} started by {year} needs {c.parent} started by {int(year) - c.parent_lag}"
    if kind == "in":
        return f"the scenario funds {rest}"
    if kind == "out":
        return f"the scenario leaves {rest} out"
    if kind == "fix":
        pid, year = rest.split("_")
        return f"the scenario starts {pid} in {year}"
    if kind == "risk":
        return f"remove at least ${request.risk_floor:,.1f}k of risk"
    return name


def explain(request: Request, rows: list[str]) -> Conflict:
    lines = [f"No plan meets these {len(rows)} rules together; drop or change any one of them:"]
    lines += [f"  {name}: {describe(request, name)}" for name in rows]
    return Conflict(rows, "\n".join(lines))


def why_infeasible(request: Request) -> Conflict | None:
    """None when the request has a plan; otherwise the rows that clash, and a message naming them."""
    built = build(request)
    if feasible(built):
        return None
    return explain(request, deletion_filter(built))


def why_deferred(request: Request, plan, project_id: str) -> Deferral:
    """What funding `project_id` would cost the plan, or which rows make it impossible."""
    built = build(request)
    built.add(f"force_{project_id}", built.started(project_id) == 1)
    forced = solve_built(built)
    if forced.status == "infeasible":
        rows = deletion_filter(built, keep=(f"force_{project_id}",))
        return Deferral(project_id, math.inf, (), explain(request, rows))
    displaced = tuple(p for p in plan.funded if p not in forced.starts)
    return Deferral(project_id, plan.npv - forced.npv, displaced, None)

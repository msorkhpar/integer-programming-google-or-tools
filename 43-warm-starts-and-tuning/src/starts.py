"""Starting plans for this cycle's model: last cycle's plan carried forward, repaired, or built greedily.

Every function here works on plans as data ({project id: start year}), never on a solver's result,
so a start can be checked, compared and saved before any solver sees it (lesson 4.3.3's design note).
"""

from __future__ import annotations

from gridcap import Portfolio

from plan_model import broken, value


def carry_forward(old: dict[str, int], pf: Portfolio) -> tuple[dict[str, int], dict[str, list[str]]]:
    """Last cycle's plan, restricted to the decisions this cycle's model still has.

    Returns the carried plan and, for the report, which old starts were kept, which have no
    variable any more, and which projects are new (no old decision to carry).
    """
    allowed = {p.project_id: set(p.starts()) for p in pf.projects}
    carried = {i: t for i, t in old.items() if t in allowed.get(i, ())}
    report = {
        "kept": sorted(carried),
        "no variable": sorted(i for i in old if i not in carried),
        "new": sorted(i for i in allowed if i.startswith("N")),
    }
    return carried, report


def repair(pf: Portfolio, plan: dict[str, int]) -> dict[str, int]:
    """Drop optional projects until the plan breaks no row.

    While a budget row is broken, drop the project with the least NPV per $k among the optional
    projects that spend in a broken year; a child goes with its parent. Must-do projects are never
    dropped: if only they are left to drop, the plan is returned as it is, and `broken` says so.
    """
    plan = dict(plan)
    by_id = {p.project_id: p for p in pf.projects}
    while rows := broken(pf, plan):
        years = {int(r.split("_")[1]) for r in rows if r.startswith("budget_")}
        optional = [i for i in plan if not by_id[i].must_do
                    and any(by_id[i].spend(plan[i]).get(y, 0) for y in years)]
        if not optional:
            break
        drop = min(optional, key=lambda i: (by_id[i].npv[plan[i]] / max(by_id[i].capex, 1), i))
        for i in [drop] + [c.project_id for c in pf.projects if c.parent == drop]:
            plan.pop(i, None)
    return plan


def greedy_fill(pf: Portfolio, plan: dict[str, int]) -> dict[str, int]:
    """Add projects the plan leaves out, best NPV per $k first, each at its earliest start that keeps the plan valid."""
    plan = dict(plan)
    order = sorted((p for p in pf.projects if p.project_id not in plan),
                   key=lambda p: (-max(p.npv.values()) / max(p.capex, 1), p.project_id))
    for p in order:
        for t in p.starts():
            plan[p.project_id] = t
            if not broken(pf, plan):
                break
            del plan[p.project_id]
    return plan


def greedy_plan(pf: Portfolio) -> dict[str, int]:
    """A plan from nothing: the must-dos at their earliest starts, then a greedy fill."""
    return greedy_fill(pf, {p.project_id: p.earliest_start for p in pf.projects if p.must_do})


def summary(pf: Portfolio, plan: dict[str, int]) -> str:
    rows = broken(pf, plan)
    return f"NPV {value(pf, plan):>7,}  {len(plan):>3} starts  breaks {', '.join(rows) if rows else 'nothing'}"

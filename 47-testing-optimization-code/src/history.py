"""GridCap's planning history, which this course invents: it is fictional, like all of GridCap.

A real back-test reads a utility's archive: the input snapshot each past planning cycle used and
the plan that cycle approved. GridCap has no past, so this module makes one up, the same way every
time:

* the snapshot of cycle Y is GridCap small generated with seed Y, its years moved to start in Y;
* the plan "approved" in cycle Y is what an earlier version of the model chose on that snapshot:
  the lump-cost shortcut of lesson 6.4.2, which charges a project's whole cost to its start year.

No number here describes a real utility or a real decision.
"""

from __future__ import annotations

from dataclasses import replace

from gridcap import Portfolio, generate
from ortools.math_opt.python import mathopt

import plan_model
from plan_model import Built, optimize

CYCLES = (2024, 2025, 2026)


def shifted(portfolio: Portfolio, offset: int) -> Portfolio:
    """The same portfolio with every year moved by `offset`."""
    projects = tuple(replace(p, earliest_start=p.earliest_start + offset, latest_start=p.latest_start + offset,
                             npv={t + offset: v for t, v in p.npv.items()}) for p in portfolio.projects)
    return replace(portfolio, name=f"{portfolio.name} {portfolio.years[0] + offset}",
                   years=tuple(y + offset for y in portfolio.years), projects=projects,
                   budget={y + offset: b for y, b in portfolio.budget.items()})


def snapshot(cycle: int) -> Portfolio:
    """The (invented) input snapshot of a past planning cycle."""
    small = generate("small", seed=cycle)
    return shifted(small, cycle - small.years[0])


def add_lump_budget(built: Built) -> None:
    """The earlier model's budget row: each project's whole cost charged to its start year."""
    by_year = {y: mathopt.LinearExpression() for y in built.portfolio.years}
    for p in built.portfolio.projects:
        for t in p.starts():
            by_year[t] += p.capex * built.x[p.project_id, t]
    for y in built.portfolio.years:
        built.model.add_linear_constraint(by_year[y] <= built.portfolio.budget[y], name=f"budget_{y}")


def approved(cycle: int) -> dict[str, int]:
    """The (invented) plan approved in a past cycle: the earlier model's optimum on its snapshot."""
    _, _, plan = optimize(snapshot(cycle), {**plan_model.RULES, "budget": add_lump_budget})
    return plan

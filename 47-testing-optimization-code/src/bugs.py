"""Five broken copies of plan_model's rules, each a mistake that real model code makes.

Each one is a single changed line of the correct function, the kind of edit a refactor or a hurried
fix leaves behind. The lessons use them to ask which tests notice.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

import plan_model
from plan_model import Built, started


def budget_skips_last_year(built: Built) -> None:
    """The loop stops one year short: `years[:-1]` where `years` was meant."""
    by_year = plan_model.spend(built)
    for y in built.portfolio.years[:-1]:
        built.model.add_linear_constraint(by_year[y] <= built.portfolio.budget[y], name=f"budget_{y}")


def must_written_as_once(built: Built) -> None:
    """A must-do row written with `<=`, so leaving the project out is allowed."""
    for p in built.portfolio.projects:
        if p.must_do:
            built.model.add_linear_constraint(started(built, p.project_id) <= 1, name=f"must_{p.project_id}")


def _after(built: Built, lag_of) -> None:
    """plan_model.add_after with the lag read through `lag_of`, so a bug can change it."""
    by_id = {p.project_id: p for p in built.portfolio.projects}
    for c in built.portfolio.projects:
        if not c.parent:
            continue
        parent = by_id[c.parent]
        for t in c.starts():
            child_by_t = mathopt.LinearExpression()
            for u in c.starts():
                if u <= t:
                    child_by_t += built.x[c.project_id, u]
            parent_by = mathopt.LinearExpression()
            for s in parent.starts():
                if s <= t - lag_of(c):
                    parent_by += built.x[parent.project_id, s]
            built.model.add_linear_constraint(child_by_t <= parent_by, name=f"after_{c.project_id}_{t}")


def after_ignores_lag(built: Built) -> None:
    """The parent's running total is taken up to year t, not t - lag."""
    _after(built, lambda c: 0)


def after_counts_lag_twice(built: Built) -> None:
    """The lag added once in the data and once more in the row: t - lag - 1, too strict."""
    _after(built, lambda c: c.parent_lag + 1)


def alt_counts_first_year_only(built: Built) -> None:
    """Each member counted only by its earliest-start variable, not by `started`."""
    groups: dict[str, list[str]] = {}
    for p in built.portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in sorted(groups.items()):
        total = mathopt.LinearExpression()
        for m in members:
            total += built.x[m, built.portfolio.project(m).earliest_start]
        built.model.add_linear_constraint(total <= 1, name=f"alt_{g}")


#: The rule each bug replaces.
BUGS = {
    "budget skips the last year": ("budget", budget_skips_last_year),
    "must-do written as <=": ("must", must_written_as_once),
    "precedence ignores the lag": ("after", after_ignores_lag),
    "alternatives count one year": ("alt", alt_counts_first_year_only),
    "precedence adds 1 to the lag": ("after", after_counts_lag_twice),
}


def broken(name: str) -> dict:
    """plan_model's rules with one of them replaced by the named bug."""
    rule, add = BUGS[name]
    return {**plan_model.RULES, rule: add}

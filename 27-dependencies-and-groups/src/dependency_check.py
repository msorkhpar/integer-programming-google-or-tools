"""Lesson 6.5.2: what the dependency graph says before any model is built.

GridCap is a fictional utility's portfolio; the planner's edits below are invented for the lesson.
"""

from dataclasses import replace

from gridcap import generate
from planning_model import build, schedule, solve_highs, status

small = generate("small")


def ancestors(portfolio, pid: str) -> list[str]:
    """Every project `pid` needs, directly or through its parents, nearest first."""
    found, here = [], portfolio.project(pid).parent
    while here is not None and here not in found and here != pid:
        found.append(here)
        here = portfolio.project(here).parent
    return found


def check(portfolio) -> list[str]:
    problems = []
    for c in portfolio.projects:
        if c.parent is None:
            continue
        p = portfolio.project(c.parent)
        if p.earliest_start + c.parent_lag > c.latest_start:
            problems.append(f"{c.project_id} can never start: {p.project_id} starts {p.earliest_start} at the "
                            f"earliest, lag {c.parent_lag}, {c.project_id} starts {c.latest_start} at the latest")
        if c.must_do:
            for a in ancestors(portfolio, c.project_id):
                if not portfolio.project(a).must_do:
                    problems.append(f"{c.project_id} is a must-do, so {a} is one too")
        if c.project_id in ancestors(portfolio, c.parent) and c.project_id < c.parent:
            problems.append(f"{c.project_id} and {c.parent} need each other: a bundle, not a parent and child")
    return problems


def edit(portfolio, pid, **changes):
    return replace(portfolio, projects=tuple(replace(p, **changes) if p.project_id == pid else p
                                            for p in portfolio.projects))


print("children:", [(c.project_id, c.parent, c.parent_lag) for c in small.projects if c.parent])
for label, portfolio in [
        ("as generated", small),
        ("P023 made a must-do", edit(small, "P023", must_do=True)),
        ("P016 lag raised to 2", edit(small, "P016", parent_lag=2)),
        ("P015 made a child of P016", edit(small, "P015", parent="P016")),
]:
    found = check(portfolio)
    print(f"{label}: {found or 'no problem found'}")
    if found:
        plan = build(portfolio)
        result = solve_highs(plan.model)
        if status(result) == "OPTIMAL":
            starts = schedule(plan, result)
            print("   solve OPTIMAL;", {i: starts.get(i, "-") for i in ("P015", "P016", "P022", "P023")})
        else:
            print("   solve", status(result))

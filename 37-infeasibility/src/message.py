"""Lesson 9.1.6: turn the rows of a conflict into a message a planner can act on.

Three steps, each a function:

* `describe` says what one row means, in the planners' words: projects by id and name, money in $k,
  and whether a number is GridCap's own or a value the scenario set;
* `arithmetic` shows why the rows clash: it tries every start year the conflict leaves to each
  project it names, and for each, the year where money or crews run out;
* `explain` puts them together: the rules, the arithmetic, and the changes that end the conflict.

GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

from itertools import product

from gridcap import Portfolio
from lock_model import Scenario, active


def label(portfolio: Portfolio, pid: str) -> str:
    return f"{pid} {portfolio.project(pid).name}"


def describe(name: str, portfolio: Portfolio, scenario: Scenario) -> str:
    kind, _, rest = name.partition("_")
    if kind == "must":
        p = portfolio.project(rest)
        years = " or ".join(str(t) for t in p.starts())
        return f"{label(portfolio, rest)} is must-do: it has to start in {years}."
    if kind == "force":
        pid, _, year = rest.partition("_")
        return f"Planners forced {label(portfolio, pid)} into the plan" + (f", starting in {year}." if year else ".")
    if kind == "after":
        pid, year = rest.rsplit("_", 1)
        c = portfolio.project(pid)
        return (f"{label(portfolio, pid)} may start in {year} only if {label(portfolio, c.parent)} "
                f"has started by {int(year) - c.parent_lag}.")
    if kind == "budget":
        year = int(rest)
        if year in scenario.budget:
            return f"Finance locked the {year} budget at ${scenario.budget[year]:,}k (GridCap's figure: ${portfolio.budget[year]:,}k)."
        return f"The {year} budget is ${portfolio.budget[year]:,}k."
    if kind == "crews":
        program, year = rest.rsplit("_", 1)
        key = (program, int(year))
        if key in scenario.crews:
            return (f"{program.capitalize()} crews have {scenario.crews[key]} crew-months in {year} in this scenario "
                    f"(GridCap's figure: {portfolio.crews[key]}).")
        return f"{program.capitalize()} crews have {portfolio.crews[key]} crew-months in {year}."
    if kind == "floor":
        return f"The {rest} region must receive at least ${portfolio.region_floor[rest]:,}k over the plan."
    if kind == "alt":
        members = [p.project_id for p in portfolio.projects if p.alt_group == rest]
        return f"At most one of {', '.join(members)} may be funded (alternatives {rest})."
    if kind == "once":
        return f"{label(portfolio, rest)} starts at most once."
    if kind == "drop":
        return f"Planners took {label(portfolio, rest)} out of the plan."
    return name


def starts(conflict: list[str], portfolio: Portfolio) -> dict[str, list[int]]:
    """Each project the conflict requires, with the start years the conflict's rows leave it."""
    years: dict[str, list[int]] = {}
    for name in conflict:
        kind, _, rest = name.partition("_")
        if kind == "must":
            years[rest] = list(portfolio.project(rest).starts())
        elif kind == "force":
            pid, _, year = rest.partition("_")
            years[pid] = [int(year)] if year else list(portfolio.project(pid).starts())
    for name in conflict:
        kind, _, rest = name.partition("_")
        if kind == "after":
            pid, year = rest.rsplit("_", 1)
            c = portfolio.project(pid)
            if pid in years and years[pid] == [int(year)]:      # the child starts in that year, so the parent is needed
                years[c.parent] = [s for s in portfolio.project(c.parent).starts() if s <= int(year) - c.parent_lag]
    return years


def use(portfolio: Portfolio, row: str, pid: str, t: int) -> int:
    """What project `pid`, started in year t, takes from the budget or crew row `row`."""
    p = portfolio.project(pid)
    kind, _, rest = row.partition("_")
    if kind == "budget":
        return p.spend(t).get(int(rest), 0)
    program, year = rest.rsplit("_", 1)
    return p.crew_months if p.program == program and active(p, t, int(year)) else 0


def capacity(portfolio: Portfolio, scenario: Scenario, row: str) -> int:
    kind, _, rest = row.partition("_")
    if kind == "budget":
        return scenario.budget.get(int(rest), portfolio.budget[int(rest)])
    program, year = rest.rsplit("_", 1)
    return scenario.crews.get((program, int(year)), portfolio.crews[program, int(year)])


def amount(row: str, value: int) -> str:
    return f"${value:,}k" if row.startswith("budget_") else f"{value} crew-months"


def resource(row: str) -> tuple[str, str]:
    """What a budget or crew row is called in a sentence, and its verb."""
    kind, _, rest = row.partition("_")
    if kind == "budget":
        return f"the {rest} budget", "has"
    program, year = rest.rsplit("_", 1)
    return f"{program} crews in {year}", "have"


def arithmetic(conflict: list[str], portfolio: Portfolio, scenario: Scenario) -> list[str]:
    """For every way to start the projects the conflict requires, the budget or crew row it breaks."""
    years = starts(conflict, portfolio)
    rows = [n for n in conflict if n.startswith(("budget_", "crews_"))]
    pids = sorted(years)
    lines = []
    for choice in product(*(years[p] for p in pids)):
        for row in rows:
            parts = {p: use(portfolio, row, p, t) for p, t in zip(pids, choice) if use(portfolio, row, p, t)}
            need, have = sum(parts.values()), capacity(portfolio, scenario, row)
            if need > have:
                when = ", ".join(f"{p} in {t}" for p, t in zip(pids, choice))
                what, verb = resource(row)
                share = " + ".join(f"{p} {amount(row, v)}" for p, v in parts.items())
                lines.append(f"Starting {when}: {what} must cover {amount(row, need)} ({share}) "
                             f"but {verb} {amount(row, have)}.")
                break
    return lines


def remedy(name: str, portfolio: Portfolio) -> str | None:
    """The change to a row that planners or finance can make, in their words; None for a model rule."""
    kind, _, rest = name.partition("_")
    if kind == "budget":
        return f"raise the {rest} budget"
    if kind == "crews":
        program, year = rest.rsplit("_", 1)
        return f"find more {program} crew-months for {year}"
    if kind == "floor":
        return f"lower the {rest} floor"
    if kind == "force":
        pid, _, year = rest.partition("_")
        return f"let {pid} start in another year" if year else f"stop forcing {pid} into the plan"
    if kind == "drop":
        return f"let {rest} back into the plan"
    return None


def explain(conflict: list[str], portfolio: Portfolio, scenario: Scenario) -> list[str]:
    """The whole message for one conflict, a line per item."""
    rows = sorted(conflict, key=lambda n: (not n.startswith(("force_", "must_")), n))
    lines = ["These rules cannot all hold:"]
    lines += [f"  - {describe(n, portfolio, scenario)}" for n in rows]
    lines += ["Why:"] + [f"  - {line}" for line in arithmetic(conflict, portfolio, scenario)]
    options = [remedy(n, portfolio) for n in rows if remedy(n, portfolio)]
    lines.append("Any one of these changes ends this conflict: " + "; ".join(options) + ".")
    return lines

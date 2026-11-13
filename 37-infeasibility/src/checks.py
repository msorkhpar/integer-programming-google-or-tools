"""Lesson 9.1.2: five checks that find known causes of infeasibility in the data, before any solve.

Each check reads only the portfolio and the scenario, and each is sound: it reports a problem only
when no plan can exist, so a scenario that has a plan never fails one. They are not complete: a
scenario can pass all five and still have no plan, because the checks look at one project, group or
region at a time, never at how they combine.

"Required" projects are the must-do projects and the ones the scenario forces in; a forced start
year narrows the project's window to that year.
"""

from __future__ import annotations

from dataclasses import dataclass

from gridcap import Portfolio
from lock_model import Scenario


@dataclass(frozen=True)
class Problem:
    check: str          # which check found it
    subject: str        # the project, group or region it is about
    detail: str         # what is wrong, with the numbers


def required(portfolio: Portfolio, scenario: Scenario) -> dict[str, list[int]]:
    """Each required project's possible start years: its window, or the forced year."""
    need = {}
    for p in portfolio.projects:
        if p.must_do or p.project_id in scenario.force_in:
            year = scenario.force_in.get(p.project_id)
            need[p.project_id] = [t for t in p.starts() if year is None or t == year]
    return need


def last_year(portfolio: Portfolio) -> int:
    return portfolio.years[-1]


def check_windows(portfolio: Portfolio, scenario: Scenario) -> list[Problem]:
    """A required project with no start year whose work fits inside the plan."""
    found = []
    for pid, starts in required(portfolio, scenario).items():
        p = portfolio.project(pid)
        fits = [t for t in starts if t >= portfolio.years[0] and t + p.duration - 1 <= last_year(portfolio)]
        if not fits:
            found.append(Problem("window", pid, f"no start year: window {p.earliest_start}-{p.latest_start}, "
                                                f"forced {scenario.force_in.get(pid)}, {p.duration} year(s) of work"))
    return found


def check_budgets(portfolio: Portfolio, scenario: Scenario) -> list[Problem]:
    """A required project that alone overspends some year's budget in every start year it may use."""
    budget = {y: scenario.budget.get(y, b) for y, b in portfolio.budget.items()}
    found = []
    for pid, starts in required(portfolio, scenario).items():
        p = portfolio.project(pid)
        if starts and all(any(amount > budget.get(y, 0) for y, amount in p.spend(t).items()) for t in starts):
            found.append(Problem("budget", pid, f"spends {list(p.cost_profile)} from its start in {starts}; "
                                                f"budgets {[budget.get(t) for t in starts]}"))
    return found


def check_crews(portfolio: Portfolio, scenario: Scenario) -> list[Problem]:
    """A required project that alone needs more crew-months than its program has, in every start year."""
    crews = {k: scenario.crews.get(k, v) for k, v in portfolio.crews.items()}
    found = []
    for pid, starts in required(portfolio, scenario).items():
        p = portfolio.project(pid)
        def short(t: int) -> bool:
            return any(p.crew_months > crews.get((p.program, y), 0) for y in range(t, t + p.duration))
        if starts and all(short(t) for t in starts):
            found.append(Problem("crews", pid, f"needs {p.crew_months} {p.program} crew-months a year; "
                                               f"{[crews.get((p.program, t)) for t in starts]} in {starts}"))
    return found


def check_groups(portfolio: Portfolio, scenario: Scenario) -> list[Problem]:
    """An alternative group (at most one member) with two or more required members."""
    need = required(portfolio, scenario)
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group and p.project_id in need:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    return [Problem("group", g, f"at most one of the group may be funded, but {members} are all required")
            for g, members in sorted(groups.items()) if len(members) > 1]


def check_floors(portfolio: Portfolio, scenario: Scenario) -> list[Problem]:
    """A region floor above everything the region's projects could spend, all of them funded."""
    found = []
    for r, floor in sorted(portfolio.region_floor.items()):
        supply = sum(p.capex for p in portfolio.projects if p.region == r and p.project_id not in scenario.force_out)
        if supply < floor:
            found.append(Problem("floor", r, f"floor ${floor:,}k, but all its projects together cost ${supply:,}k"))
    return found


CHECKS = (check_windows, check_budgets, check_crews, check_groups, check_floors)


def run_checks(portfolio: Portfolio, scenario: Scenario = Scenario()) -> list[Problem]:
    return [problem for check in CHECKS for problem in check(portfolio, scenario)]

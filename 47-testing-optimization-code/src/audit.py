"""Re-check a plan against the data, in plain Python, without the model.

A test that asks the model whether its own plan is valid asks the suspect to judge itself. This
checker reads only the portfolio and the plan, so a rule written wrong in the model and a rule
written wrong here would have to be wrong in the same way for a bad plan to pass both.
"""

from __future__ import annotations

from gridcap import Portfolio


def spend_by_year(portfolio: Portfolio, plan: dict[str, int]) -> dict[int, int]:
    """What the plan spends in each year of the horizon, in $k (integers, so exact)."""
    spend = {y: 0 for y in portfolio.years}
    for pid, start in plan.items():
        for year, amount in portfolio.project(pid).spend(start).items():
            spend[year] = spend.get(year, 0) + amount
    return spend


def violations(portfolio: Portfolio, plan: dict[str, int]) -> list[str]:
    """Every rule the plan breaks, one line each; an empty list means the plan is valid."""
    found = []
    ids = set(portfolio.project_ids)
    for pid, start in sorted(plan.items()):
        if pid not in ids:
            found.append(f"{pid}: no such project")
        elif start not in portfolio.project(pid).starts():
            found.append(f"{pid}: starts {start}, outside its window")
    if found:
        return found
    for p in portfolio.projects:
        if p.must_do and p.project_id not in plan:
            found.append(f"{p.project_id}: must-do not funded")
        if p.parent and p.project_id in plan:
            if p.parent not in plan:
                found.append(f"{p.project_id}: funded without its parent {p.parent}")
            elif plan[p.project_id] < plan[p.parent] + p.parent_lag:
                found.append(f"{p.project_id}: starts {plan[p.project_id]}, before {p.parent} + {p.parent_lag}")
    groups: dict[str, list[str]] = {}
    for pid in plan:
        group = portfolio.project(pid).alt_group
        if group:
            groups.setdefault(group, []).append(pid)
    for group, members in sorted(groups.items()):
        if len(members) > 1:
            found.append(f"{group}: {len(members)} alternatives funded ({', '.join(sorted(members))})")
    for year, amount in spend_by_year(portfolio, plan).items():
        if year in portfolio.budget and amount > portfolio.budget[year]:
            found.append(f"{year}: spends {amount:,} over the budget of {portfolio.budget[year]:,}")
    return found


def value(portfolio: Portfolio, plan: dict[str, int]) -> int:
    """The plan's NPV recomputed from the data, in $k."""
    return sum(portfolio.project(pid).npv[start] for pid, start in plan.items())

"""Why a project is in or out of GridCap's best plan: force the opposite, re-solve, and read the rules (lesson 9.3.2)."""

from __future__ import annotations

from dataclasses import dataclass, replace

from gridcap import Portfolio

from binding import refusals, slack_table
from explain_model import Run, Scenario, build, solve


@dataclass
class Forced:
    pid: str
    action: str                     # "in", "out" or "at <year>"
    status: str
    cost: int | None                # base NPV less forced NPV, $k; None when the forcing is infeasible
    plan: dict[str, int]


def changes(a: dict[str, int], b: dict[str, int]) -> tuple[list[str], list[str], list[str]]:
    """Projects added, dropped and moved from plan a to plan b (lesson 9.3.3 builds the full diff)."""
    added = sorted(set(b) - set(a))
    dropped = sorted(set(a) - set(b))
    moved = [f"{p} {a[p]}->{b[p]}" for p in sorted(set(a) & set(b)) if a[p] != b[p]]
    return added, dropped, moved


def force(portfolio: Portfolio, scenario: Scenario, base: Run, pid: str, year: int | None = None) -> Forced:
    """Re-solve with the decision on `pid` reversed: in if it is out, out if it is in, or pinned to `year`."""
    if year is not None:
        action, changed = f"at {year}", replace(scenario, force_in={**scenario.force_in, pid: year})
    elif pid in base.plan:
        action, changed = "out", replace(scenario, force_out=scenario.force_out | {pid})
    else:
        action, changed = "in", replace(scenario, force_in={**scenario.force_in, pid: None})
    run = solve(build(portfolio, changed))
    cost = None if run.npv is None else round(base.npv - run.npv)
    return Forced(pid, action, run.status, cost, run.plan)


def rule_facts(portfolio: Portfolio, base: Run, pid: str) -> list[dict]:
    """The rows that refuse adding an unfunded project to the plan as it stands, in any start year.

    One fact per row: an alternative row names the option already funded; a budget row gives the
    room left and the least the project would need there, over the start years that use the row.
    """
    refused = refusals(base.built, base.plan)
    room = {name: s for name, _, s in slack_table(base.built, base.plan)}
    project = portfolio.project(pid)
    need: dict[str, int] = {}
    for t in project.starts():
        for name in refused[pid, t]:
            amount = project.spend(t)[int(name[-4:])] if name.startswith("budget_") else 0
            need[name] = min(need.get(name, amount), amount)
    facts = []
    for name in sorted(need, key=lambda n: (not n.startswith("alt_"), n)):
        if name.startswith("alt_"):
            taken = [p.project_id for p in portfolio.projects
                     if p.alt_group == project.alt_group and p.project_id in base.plan]
            facts.append({"row": name, "funded": taken})
        else:
            facts.append({"row": name, "year": int(name[-4:]), "left": round(room[name]), "needs": need[name]})
    return facts


def rules_against(portfolio: Portfolio, base: Run, pid: str) -> list[str]:
    """`rule_facts` as one line per row."""
    return [f"{f['row']}: {', '.join(f['funded'])} already funded" if "funded" in f
            else f"{f['row']}: {f['left']:,} left, needs at least {f['needs']:,}"
            for f in rule_facts(portfolio, base, pid)]

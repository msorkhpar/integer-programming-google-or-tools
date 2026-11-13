"""LNS around a MIP solver: free one neighborhood of a plan, keep the rest, re-solve, keep what is better."""

from __future__ import annotations

from gridcap import Portfolio

from capital import EXACT, build, schedule, solve_highs, value
from rolling import fix

REGIONS = ("Ridge", "Valley", "Coast", "Plains")


def neighborhoods(portfolio: Portfolio, plan: dict[str, int], kind: str, index: int) -> tuple[str, set[str]]:
    """The projects a step frees. "region": one region's projects; "years": every project that starts,
    or could start, in a run of three years."""
    if kind == "region":
        r = REGIONS[index % len(REGIONS)]
        return r, {p.project_id for p in portfolio.projects if p.region == r}
    first = portfolio.years[(2 * index) % (len(portfolio.years) - 2)]
    span = range(first, first + 3)
    free = {p.project_id for p in portfolio.projects
            if (p.project_id in plan and plan[p.project_id] in span)
            or (p.project_id not in plan and any(t in span for t in p.starts()))}
    return f"{first}-{first + 2}", free


def lns(portfolio: Portfolio, start: dict[str, int], kind: str, steps: int, *, verbose: bool = True):
    cap = build(portfolio, crews=True)
    current, best = dict(start), value(portfolio, start)
    nodes = 0
    for k in range(steps):
        name, free = neighborhoods(portfolio, current, kind, k)
        for (pid, t), var in cap.x.items():
            if pid in free:
                var.lower_bound, var.upper_bound = 0, 1
            else:
                fix(var, 1 if current.get(pid) == t else 0)       # outside the neighborhood: keep the plan
        result = solve_highs(cap.model, EXACT)
        found = schedule(cap, result)
        nodes += result.solve_stats.node_count
        if value(portfolio, found) > best:
            current, best = found, value(portfolio, found)
        if verbose:
            print(f"  step {k + 1:2} free {name:9} ({len(free):3} projects)  plan {best:,}")
    return current, nodes

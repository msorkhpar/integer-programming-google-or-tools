"""Roll a regional plan forward one planning cycle, the way a utility re-plans every year.

A capital plan is used in a rolling format: it is solved, its first year is carried out, and a
year later the model is slid forward one year with better data and solved again. `next_cycle`
makes the next year's model from this year's portfolio and approved plan:

- the projects the plan starts in the first year are now committed: they leave the decisions, and
  what they still spend is taken off the later years' budgets;
- the horizon drops its first year and gains one at the end (budgeted like the old last year);
- a project whose window has passed without a start drops out, and so does a child whose parent
  can no longer start; a child of a committed parent keeps its lag as an earliest start;
- the new data: each year's budget revised by -3% to +3%, about one project in eight costing 20%
  more (its NPV falls by the extra cost), and five new candidate projects.

All of it is drawn from `random.Random(seed)`, so the same inputs give the same next cycle.
GridCap is fictional.
"""

from __future__ import annotations

import random
from dataclasses import replace

from gridcap import Portfolio, Project, generate

NEW_PROJECTS = 5


def _rounded(amount: float) -> int:
    return int(10 * round(amount / 10))


def next_cycle(pf: Portfolio, plan: dict[str, int], seed: int) -> tuple[Portfolio, set[str]]:
    """Next year's portfolio, and the projects this year's plan committed."""
    rng = random.Random(seed)
    first = pf.years[0]
    years = pf.years[1:] + (pf.years[-1] + 1,)
    committed = {i for i, t in plan.items() if t == first}
    budget = {y: pf.budget[y] for y in pf.years[1:]}
    budget[years[-1]] = pf.budget[pf.years[-1]]
    for i in committed:
        for y, amount in pf.project(i).spend(first).items():
            if y in budget:
                budget[y] -= amount
    budget = {y: max(0, _rounded(b * (0.97 + 0.06 * rng.random()))) for y, b in budget.items()}

    kept: dict[str, Project] = {}
    for p in pf.projects:                       # parents come before their children in GridCap
        if p.project_id in committed:
            continue
        earliest = max(p.earliest_start, years[0])
        parent, lag = p.parent, p.parent_lag
        if parent in committed:                 # the parent started in `first`: the lag is now a date
            earliest, parent, lag = max(earliest, first + p.parent_lag), None, 0
        elif parent is not None and parent not in kept:
            continue                            # the parent can no longer start, so neither can the child
        if earliest > p.latest_start:
            continue                            # the window has passed
        cost, npv = p.cost_profile, dict(p.npv)
        if rng.random() < 0.125:
            cost = tuple(_rounded(c * 1.2) for c in p.cost_profile)
            extra = sum(cost) - sum(p.cost_profile)
            npv = {t: v - extra for t, v in npv.items()}
        kept[p.project_id] = replace(p, earliest_start=earliest, parent=parent, parent_lag=lag,
                                     cost_profile=cost, npv={t: v for t, v in npv.items() if t >= earliest})

    region = pf.projects[0].region
    donors = [p for p in generate("medium", seed).projects
              if p.region == region and p.parent is None and p.alt_group is None and not p.must_do
              and p.latest_start >= years[0]]
    for n, p in enumerate(rng.sample(donors, NEW_PROJECTS), start=1):
        earliest = max(p.earliest_start, years[0])
        kept[f"N{n:03d}"] = replace(p, project_id=f"N{n:03d}", earliest_start=earliest,
                                    npv={t: v for t, v in p.npv.items() if t >= earliest})
    return replace(pf, name=f"{pf.name} next", years=years, budget=budget,
                   projects=tuple(kept.values())), committed

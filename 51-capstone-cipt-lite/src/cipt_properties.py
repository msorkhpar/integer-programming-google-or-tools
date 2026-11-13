"""CIPT Lite, milestone 5: Hypothesis properties of the whole model, on portfolios drawn feasible by construction.

`portfolios()` draws a small portfolio with every rule the model has (must-dos, parents with lags,
alternatives, yearly, regional and crew limits, regional floors) around a witness plan, so every
drawn case has a plan (lesson 12.3.2). `holds(case, builder)` solves it and checks, from the data
alone, that the plan breaks no rule, that the reported value is the plan's, that it is no worse than
the witness, and that more money never lowers the value. These portfolios are invented test data.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from hypothesis import settings
from hypothesis import strategies as st

from cipt_model import Scenario, build, check, npv_of, params, plan_of, solve
from gridcap import Asset, Portfolio, Project

YEARS = (2027, 2028, 2029)
REGIONS = ("North", "South")
PROGRAMS = ("transmission", "distribution")
CI = settings(max_examples=200, derandomize=True, database=None, deadline=None)


@dataclass(frozen=True)
class Case:
    portfolio: Portfolio
    witness: dict[str, int]


def worth(value: int, starts: int) -> list[int]:
    """NPV by start year, $5k less for each year of delay, as most real projects lose value waiting."""
    return [value - 5 * k for k in range(starts)]


@st.composite
def portfolios(draw, max_projects: int = 8) -> Case:
    n = draw(st.integers(1, max_projects))
    projects: list[Project] = []
    witness: dict[str, int] = {}
    used_groups: set[str] = set()
    for k in range(n):
        pid = f"P{k + 1}"
        cost = tuple(draw(st.lists(st.integers(1, 9).map(lambda c: 10 * c), min_size=1, max_size=2)))
        last_start = YEARS[-1] - len(cost) + 1
        first = draw(st.integers(YEARS[0], last_start))
        last = draw(st.integers(first, last_start))
        parent, lag = None, 0
        if projects and draw(st.booleans()):
            parent = draw(st.sampled_from([p.project_id for p in projects]))
            lag = draw(st.integers(0, 1))
        group = draw(st.sampled_from([None, None, "G1"]))
        start = draw(st.integers(first, last))
        fits = (parent is None or (parent in witness and witness[parent] + lag <= start)) \
            and group not in used_groups
        chosen = fits and draw(st.booleans())
        if chosen:
            witness[pid] = start
            if group:
                used_groups.add(group)
        projects.append(Project(
            project_id=pid, name=f"drawn project {pid}", program=draw(st.sampled_from(PROGRAMS)),
            region=draw(st.sampled_from(REGIONS)), asset_id=f"A{k + 1}", intervention="replace",
            cost_profile=cost, earliest_start=first, latest_start=last, must_do=chosen and draw(st.booleans()),
            parent=parent, parent_lag=lag, alt_group=group, crew_months=draw(st.integers(1, 3)),
            npv=dict(zip(range(first, last + 1), worth(draw(st.integers(-5, 100)), last - first + 1)))))
    by_id = {p.project_id: p for p in projects}
    spend = {y: 0 for y in YEARS}
    region = {(r, y): 0 for r in REGIONS for y in YEARS}
    crews = {(g, y): 0 for g in PROGRAMS for y in YEARS}
    funded = {r: 0 for r in REGIONS}
    for pid, t in witness.items():
        p = by_id[pid]
        funded[p.region] += p.capex
        for y, amount in p.spend(t).items():
            spend[y] += amount
            region[p.region, y] += amount
            crews[p.program, y] += p.crew_months
    # Each limit is tight (a little above the witness's use) or loose, so every rule gets to bind
    # in some cases and to leave the plan free in others.
    slack = st.one_of(st.integers(0, 4).map(lambda s: 10 * s), st.just(1_000))
    crew_slack = st.one_of(st.integers(0, 2), st.just(100))
    pf = Portfolio(
        name="drawn", seed=0, years=YEARS, discount_rate=0.07, projects=tuple(projects),
        assets=tuple(Asset(f"A{k + 1}", "pole", projects[k].region, 10, 2.0, 30.0, 10, 100) for k in range(n)),
        capital_budget=0, budget={y: v + draw(slack) for y, v in spend.items()},
        region_budget={k: v + draw(slack) for k, v in region.items()},
        region_floor={r: max(0, v - draw(slack)) for r, v in funded.items()},
        crews={k: v + draw(crew_slack) for k, v in crews.items()})
    return Case(pf, witness)


def holds(case: Case, builder=build) -> None:
    """Every property of one drawn case; an AssertionError names the one that failed."""
    pf = case.portfolio
    b = builder(pf)
    result = solve(b.model, params(gap=0.0))
    assert result.termination.reason.name == "OPTIMAL", f"no plan: {result.termination.reason.name}"
    plan = plan_of(b, result)
    assert check(pf, Scenario(), plan) == [], f"plan {plan} breaks {check(pf, Scenario(), plan)}"
    assert abs(result.objective_value() - npv_of(pf, plan)) < 1e-3, "reported value is not the plan's"
    assert npv_of(pf, plan) >= npv_of(pf, case.witness), "worse than the witness"
    richer = replace(pf, budget={y: v + 10 for y, v in pf.budget.items()})
    more = solve(builder(richer).model, params(gap=0.0)).objective_value()
    assert more >= result.objective_value() - 1e-3, "more budget lowered the value"

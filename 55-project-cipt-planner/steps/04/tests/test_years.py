"""Lesson 14.2.2: start years, windows and yearly budgets with spread costs."""

from cipt.data import load_request
from cipt.report import render
from cipt.solve import solve
from conftest import export, row

YEARS = (2027, 2028)


def spent(raw, plan):
    """Each year's spend, computed from the export's rows, not from the planner's code."""
    profile = {r["id"]: r["cost_profile"] for r in raw["projects"]}
    spend = {y: 0 for y in raw["years"]}
    for pid, start in plan.starts.items():
        for k, amount in enumerate(profile[pid]):
            spend[start + k] += amount
    return spend


def test_spread_cost_counts_in_every_year_of_work():
    # A spends 50 in each of two years. Funding A and B fits the two-year total but not 2028.
    raw = export([row("A", (50, 50), 80), row("B", (50,), 40), row("C", (100,), 100, earliest=2028)],
                 years=YEARS, budget={2027: 100, 2028: 100})
    plan = solve(load_request(raw))
    assert plan.funded == ("B", "C")
    assert all(spent(raw, plan)[y] <= 100 for y in YEARS)


def test_each_year_stays_within_its_budget():
    raw = export([row("A", (100,), 50, latest=2028), row("B", (100,), 50, latest=2028)],
                 years=YEARS, budget={2027: 100, 2028: 100})
    plan = solve(load_request(raw))
    assert plan.funded == ("A", "B")
    assert spent(raw, plan) == {2027: 100, 2028: 100}


def test_start_stays_inside_the_window():
    raw = export([row("A", (100,), 50, latest=2028)], years=YEARS, budget={2027: 0, 2028: 100})
    assert solve(load_request(raw)).starts == {"A": 2028}


def test_work_must_end_inside_the_plan():
    # A two-year project that may only start in the plan's last year has no start to choose.
    raw = export([row("A", (50, 50), 80, earliest=2028)], years=YEARS)
    assert solve(load_request(raw)).funded == ()


def test_report_shows_spend_against_each_budget():
    raw = export([row("A", (100,), 50, latest=2028)], years=YEARS, budget={2027: 0, 2028: 100})
    request = load_request(raw)
    text = render(request, solve(request))
    assert "  2027  spend $0k of $0k" in text
    assert "  2028  spend $100k of $100k" in text

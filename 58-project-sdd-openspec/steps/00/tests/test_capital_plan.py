"""The planner's rules, each on a hand-made portfolio of one to five projects."""

from itertools import product

from capplan.plan import allows, plan
from capplan.portfolio import Project
from capplan.request import Request


def project(pid, cost, value=100, region="north", earliest=2027, latest=2029):
    return Project(pid, region, cost, value, earliest, latest)


def test_spending_up_to_the_budget_is_allowed():
    projects = [project("A", 600), project("B", 400)]
    assert allows(projects, Request(budget=1000, years=3), {("A", 2027), ("B", 2027)})


def test_spending_over_the_budget_is_refused():
    projects = [project("A", 600), project("B", 410)]
    assert not allows(projects, Request(budget=1000, years=3), {("A", 2027), ("B", 2027)})


def test_a_project_started_twice_is_refused():
    projects = [project("A", 100)]
    request = Request(budget=1000, years=3)
    assert allows(projects, request, {("A", 2027)})
    assert not allows(projects, request, {("A", 2027), ("A", 2028)})


def test_a_start_outside_the_window_is_refused():
    projects = [project("A", 100, earliest=2028, latest=2028)]
    request = Request(budget=1000, years=3)
    assert allows(projects, request, {("A", 2028)})
    assert not allows(projects, request, {("A", 2027)})
    assert not allows(projects, request, {("A", 2030)})       # after the plan's last year


def test_more_starts_than_the_cap_are_refused():
    projects = [project(pid, 10) for pid in "ABCD"]
    request = Request(budget=1000, years=3)
    assert allows(projects, request, {("A", 2027), ("B", 2027), ("C", 2027)})
    assert not allows(projects, request, {(pid, 2027) for pid in "ABCD"})


def test_the_plan_has_the_greatest_value_within_the_rules():
    projects = [project("A", 600, 900, latest=2028), project("B", 500, 700, earliest=2028),
                project("C", 400, 500), project("D", 350, 420), project("E", 300, 310, latest=2027)]
    request = Request(budget=1000, years=2)
    best = 0
    for choice in product([None, 2027, 2028], repeat=len(projects)):
        spend = {2027: 0, 2028: 0}
        fits = True
        for p, year in zip(projects, choice):
            if year is not None:
                fits &= p.earliest <= year <= p.latest
                spend[year] += p.cost
        if fits and max(spend.values()) <= request.budget:
            best = max(best, sum(p.value for p, year in zip(projects, choice) if year is not None))
    assert plan(projects, request).value == best

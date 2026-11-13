"""The planner's rules, each on a hand-made portfolio of one to five projects."""

from itertools import product

from capplan.plan import allows, plan
from capplan.portfolio import Project
from capplan.request import Request
from capplan.report import share_by_year


def project(pid, cost, value=100, region="north", earliest=2027, latest=2029):
    return Project(pid, region, cost, value, earliest, latest)


def refusal(call):
    """The message of the ValueError a call raises, or None when it raises none."""
    try:
        call()
    except ValueError as error:
        return str(error)
    return None


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


def test_a_share_is_kept_at_its_boundary():
    projects = [project("P", 250, region="plains"), project("N", 750), project("M", 10)]
    request = Request(budget=5000, years=3, shares={"plains": 25})
    assert allows(projects, request, {("P", 2027), ("N", 2027)})                    # 250 of 1,000
    assert not allows(projects, request, {("P", 2027), ("N", 2027), ("M", 2027)})   # 250 of 1,010


def test_a_year_with_no_spend_keeps_the_share():
    projects = [project("P", 250, region="plains"), project("N", 750)]
    request = Request(budget=5000, years=3, shares={"plains": 25})
    assert allows(projects, request, {("P", 2027), ("N", 2027)})        # 2028 and 2029 spend nothing
    assert not allows(projects, request, {("P", 2027), ("N", 2028)})    # 2028: plains 0 of 750


def test_the_plan_keeps_every_share():
    projects = [project("N1", 600, 1000), project("N2", 400, 600), project("P1", 300, 200, region="plains")]
    request = Request(budget=1000, years=1, shares={"plains": 25})
    got = plan(projects, request)
    assert got.starts == {"N1": 2027, "P1": 2027}
    assert all(share >= 25 for share in share_by_year(projects, got.starts, "plains").values())


def test_a_share_outside_0_to_100_is_refused():
    projects = [project("P", 100, region="plains"), project("C", 100, region="coast")]
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, shares={"plains": 101}))) is not None
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, shares={"plains": -5}))) is not None
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, shares={"plains": 100}))) is None


def test_shares_adding_up_to_more_than_100_are_refused():
    projects = [project("P", 100, region="plains"), project("C", 100, region="coast")]
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, shares={"plains": 60, "coast": 50}))) is not None
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, shares={"plains": 40, "coast": 60}))) is None


def test_a_share_for_a_region_with_no_project_is_refused():
    projects = [project("P", 100, region="plains"), project("N", 100)]
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, shares={"coast": 10}))) is not None
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, shares={"plains": 10}))) is None

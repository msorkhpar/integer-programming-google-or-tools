"""The planner's rules, each on a hand-made portfolio of one to five projects."""

from itertools import product

from capplan.plan import allows, plan
from capplan.portfolio import Project
from capplan.request import Request
from capplan.report import overrides, share_by_year


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


def must_do_portfolio():
    return [project("A", 600, 1000), project("B", 400, 600), project("L", 300, 50)]


def test_a_must_do_project_is_started():
    request = Request(budget=1000, years=1, must_do={"L": "Regulator order RO-7"})
    assert plan(must_do_portfolio(), request).starts == {"A": 2027, "L": 2027}


def test_a_plan_without_the_must_do_is_refused():
    request = Request(budget=1000, years=1, must_do={"L": "Regulator order RO-7"})
    assert allows(must_do_portfolio(), request, {("A", 2027), ("L", 2027)})
    assert not allows(must_do_portfolio(), request, {("A", 2027), ("B", 2027)})


def test_an_override_with_an_empty_reason_is_refused():
    assert refusal(lambda: plan(must_do_portfolio(), Request(budget=1000, years=1, must_do={"L": ""}))) is not None
    assert refusal(lambda: plan(must_do_portfolio(), Request(budget=1000, years=1, must_do={"L": "RO-7"}))) is None


def test_a_reason_of_only_spaces_is_refused():
    assert refusal(lambda: plan(must_do_portfolio(), Request(budget=1000, years=1, must_do={"L": "   "}))) is not None


def test_an_override_for_an_unknown_project_is_refused():
    assert refusal(lambda: plan(must_do_portfolio(), Request(budget=1000, years=1, must_do={"Z": "RO-7"}))) is not None


def test_the_report_lists_each_override_with_its_reason():
    request = Request(budget=1000, years=1, must_do={"L": "Regulator order RO-7", "A": "Storm damage"})
    assert overrides(request) == ["A: Storm damage", "L: Regulator order RO-7"]


def test_unspent_money_carries_into_the_next_year():
    projects = [project("A", 800), project("B", 1200), project("C", 10)]
    request = Request(budget=1000, years=2, carry=20)
    assert allows(projects, request, {("A", 2027), ("B", 2028)})                    # 2028: 1,200 of 1,000 + 200
    assert not allows(projects, request, {("A", 2027), ("B", 2028), ("C", 2028)})   # 2028: 1,210


def test_carry_over_above_its_cap_is_refused():
    projects = [project("A", 500), project("B", 1200), project("C", 1250)]
    request = Request(budget=1000, years=2, carry=20)
    assert allows(projects, request, {("A", 2027), ("B", 2028)})        # 500 unspent, 200 of it carried
    assert not allows(projects, request, {("A", 2027), ("C", 2028)})    # 1,250 needs 250 carried


def test_money_cannot_be_borrowed_from_a_later_year():
    projects = [project("A", 900), project("B", 1100), project("C", 1100), project("D", 900)]
    request = Request(budget=1000, years=2, carry=20)
    assert allows(projects, request, {("A", 2027), ("B", 2028)})        # 100 carried forward
    assert not allows(projects, request, {("C", 2027), ("D", 2028)})    # 2027 would borrow 100 from 2028


def test_a_carry_over_outside_0_to_100_percent_is_refused():
    projects = [project("A", 100)]
    assert refusal(lambda: plan(projects, Request(budget=1000, years=2, carry=101))) is not None
    assert refusal(lambda: plan(projects, Request(budget=1000, years=2, carry=-1))) is not None
    assert refusal(lambda: plan(projects, Request(budget=1000, years=2, carry=100))) is None


def test_four_starts_in_one_year_are_allowed():
    projects = [project(pid, 10) for pid in "ABCD"]
    assert allows(projects, Request(budget=1000, years=3), {(pid, 2027) for pid in "ABCD"})


def test_a_request_that_sets_the_retired_cap_is_refused():
    projects = [project("A", 10)]
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, max_starts=3))) is not None
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3))) is None


def test_a_retired_cap_of_zero_is_refused_too():
    projects = [project("A", 10)]
    assert refusal(lambda: plan(projects, Request(budget=1000, years=3, max_starts=0))) is not None

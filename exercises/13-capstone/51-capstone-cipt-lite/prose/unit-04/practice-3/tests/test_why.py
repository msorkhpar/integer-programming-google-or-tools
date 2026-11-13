import pytest

from why import cost_interval, forcing_cost, refused_by


def project(program, region, cost, earliest, latest, npv, must=False, crews=1):
    return {"program": program, "region": region, "cost": cost, "earliest": earliest, "latest": latest,
            "must": must, "parent": None, "lag": 0, "group": None, "crews": crews, "npv": npv}


# A fictional utility's practice portfolio (money in $k).
SNAPSHOT = {
    "years": [2027, 2028, 2029],
    "rate": 0.05,
    "budget": {2027: 300, 2028: 300, 2029: 300},
    "region_budget": {"North": {2027: 300, 2028: 300, 2029: 300}, "South": {2027: 300, 2028: 300, 2029: 300}},
    "crews": {"lines": {2027: 3, 2028: 3, 2029: 3}, "poles": {2027: 2, 2028: 2, 2029: 2}},
    "floor": {"North": 0, "South": 0},
    "projects": {
        "J1": project("lines", "North", [200], 2027, 2028, {2027: 100, 2028: 90}, must=True),
        "J2": project("poles", "South", [250], 2027, 2029, {2027: 120, 2028: 110, 2029: 100}),
        "J3": project("lines", "North", [150, 100], 2027, 2028, {2027: 80, 2028: 70}),
        "J4": project("poles", "South", [280], 2027, 2029, {2027: 60, 2028: 55, 2029: 50}),
        "J5": project("poles", "South", [90], 2027, 2028, {2027: 30, 2028: 25}, crews=2),
    },
}
BASE = {"name": "base"}
# The best plan: NPV 300.
PLAN = {"J1": 2028, "J2": 2029, "J3": 2027, "J5": 2027}


def test_forcing_the_deferred_project_in_costs_what_the_best_plan_loses():
    forced = forcing_cost(SNAPSHOT, BASE, "J4")
    assert forced is not None
    assert forced.cost == pytest.approx(10.0, abs=1e-6)
    assert "J3 dropped" in forced.gives_way


def test_each_start_is_refused_by_the_rows_of_the_plan_as_it_stands():
    assert refused_by(SNAPSHOT, BASE, PLAN, "J4") == {
        2027: ["budget_2027", "region_South_2027", "crews_poles_2027"],
        2028: ["budget_2028"],
        2029: ["budget_2029", "region_South_2029"]}


def test_what_gives_way_lists_moves_as_well_as_drops():
    assert forcing_cost(SNAPSHOT, BASE, "J4").gives_way == ["J1 2028->2027", "J2 2029->2028", "J3 dropped"]


def test_a_forcing_no_plan_allows_has_no_price():
    no_poles = {"name": "no-poles", "crews": {"poles": {2027: 0, 2028: 0, 2029: 0}}}
    assert forcing_cost(SNAPSHOT, no_poles, "J4") is None


def test_with_gaps_the_cost_lies_between_the_bounds_of_the_two_solves():
    assert cost_interval(219_054, 219_273, 218_700, 218_900) == pytest.approx((154, 573))


def test_the_low_end_is_never_below_zero():
    assert cost_interval(100, 110, 99, 105) == pytest.approx((0, 11))


def test_rows_the_plan_already_breaks_are_listed_at_every_start():
    without_j1 = {j: t for j, t in PLAN.items() if j != "J1"}
    refused = refused_by(SNAPSHOT, BASE, without_j1, "J4")
    assert refused.get(2028) == ["must_J1", "budget_2028"]
    assert all(rows[:1] == ["must_J1"] for rows in refused.values())

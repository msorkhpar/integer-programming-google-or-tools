from renewal.fleet import Transformer
from renewal.plan import feasible, plan
from renewal.request import Request


def unit(tid, cost=500, cof=2000, age=55):
    return Transformer(tid, "S0001", "north", "small", age, cost, cof, 50, 0.0)


def test_each_year_keeps_to_its_own_budget():
    fleet = [unit("A", 600), unit("B", 600)]
    request = Request(budget=1000, years=2)
    assert feasible(fleet, request, {"A": 2027, "B": 2028})
    assert not feasible(fleet, request, {"A": 2027, "B": 2027})


def test_a_tight_budget_spreads_replacements_over_the_years():
    fleet = [unit("A"), unit("B"), unit("C")]
    got = plan(fleet, Request(budget=600, years=3, window=10))
    assert sorted(got.replace.values()) == [2027, 2028, 2029]


def test_the_riskier_unit_goes_first():
    fleet = [unit("A", cof=2000), unit("B", cof=6000)]
    got = plan(fleet, Request(budget=500, years=2, window=10))
    assert got.replace == {"B": 2027, "A": 2028}


def test_units_younger_than_the_screen_are_not_candidates():
    fleet = [unit("A", age=30, cof=90000), unit("B", age=50)]
    got = plan(fleet, Request(budget=500, years=1, window=10, min_age=40))
    assert got.replace == {"B": 2027}

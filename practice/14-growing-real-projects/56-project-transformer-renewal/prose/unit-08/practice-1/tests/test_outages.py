from renewal.fleet import Transformer
from renewal.plan import feasible, plan
from renewal.report import spend_by_year
from renewal.request import Request


def unit(tid, substation, region="north", cost=400, cof=2000):
    return Transformer(tid, substation, region, "small", 55, cost, cof, 50, 0.0)


def test_one_outage_serves_every_replacement_at_its_substation_that_year():
    fleet = [unit("A", "S1"), unit("B", "S1"), unit("C", "S2")]
    request = Request(budget=1100, outage_cost=300)
    assert feasible(fleet, request, {"A": 2027, "B": 2027})          # 400 + 400 + one outage 300
    assert not feasible(fleet, request, {"A": 2027, "C": 2027})      # 400 + 400 + two outages 600


def test_the_plan_bundles_replacements_at_one_substation():
    fleet = [unit("A", "S1", cost=300), unit("B", "S1", cost=300), unit("C", "S2", cost=300)]
    got = plan(fleet, Request(budget=900, outage_cost=300))
    assert sorted(got.replace) == ["A", "B"]


def test_a_region_takes_a_limited_number_of_outages_a_year():
    fleet = [unit("A", "S1"), unit("B", "S2"), unit("C", "S3", region="south")]
    request = Request(budget=5000, years=2, outages=1)
    assert feasible(fleet, request, {"A": 2027, "B": 2028, "C": 2027})
    assert not feasible(fleet, request, {"A": 2027, "B": 2027})


def test_spend_counts_each_outage_once():
    fleet = [unit("A", "S1"), unit("B", "S1"), unit("C", "S2")]
    spend = spend_by_year(fleet, {"A": 2027, "B": 2027, "C": 2028}, outage_cost=300)
    assert spend == {2027: 1100, 2028: 700}

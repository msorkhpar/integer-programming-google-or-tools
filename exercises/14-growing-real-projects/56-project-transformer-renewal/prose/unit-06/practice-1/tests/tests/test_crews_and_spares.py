from renewal.fleet import Transformer
from renewal.plan import feasible, plan
from renewal.request import Request


def unit(tid, kind="small", region="north", cost=300):
    return Transformer(tid, f"S-{tid}", region, kind, 55, cost, 2000, 50, 0.0)


def test_a_region_has_only_its_crew_weeks_each_year():
    fleet = [unit("A"), unit("B", "medium"), unit("C"), unit("D", region="south")]
    request = Request(budget=5000, crew_weeks=6)       # small takes 2 crew-weeks, medium 4
    assert feasible(fleet, request, {"A": 2027, "B": 2027, "D": 2027})
    assert not feasible(fleet, request, {"A": 2027, "B": 2027, "C": 2027})


def test_short_crews_push_work_into_later_years():
    fleet = [unit("A"), unit("B")]
    got = plan(fleet, Request(budget=5000, years=2, window=10, crew_weeks=2))
    assert sorted(got.replace.values()) == [2027, 2028]


def test_a_unit_needed_before_its_lead_time_must_be_a_spare():
    fleet = [unit("A", "large"), unit("B", "large")]    # a large unit takes three years to arrive
    none_in_stock = Request(budget=9000, years=4, lead_times=True)
    assert not feasible(fleet, none_in_stock, {"A": 2029})
    assert feasible(fleet, none_in_stock, {"A": 2030})
    one_in_stock = Request(budget=9000, years=4, lead_times=True, spares={"large": 1})
    assert feasible(fleet, one_in_stock, {"A": 2027, "B": 2030})
    assert not feasible(fleet, one_in_stock, {"A": 2027, "B": 2029})

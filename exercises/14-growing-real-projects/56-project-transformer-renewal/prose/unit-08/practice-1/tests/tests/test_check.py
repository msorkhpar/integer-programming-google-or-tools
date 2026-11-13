from renewal.check import violations
from renewal.fleet import Transformer
from renewal.request import Request


def unit(tid, kind="small", region="north", cost=400):
    return Transformer(tid, f"S-{tid}", region, kind, 55, cost, 2000, 50, 0.0)


def test_the_checker_names_each_broken_rule_and_passes_a_good_plan():
    fleet = [unit("A"), unit("B"), unit("C", "large"), unit("D", region="south")]
    request = Request(budget=1000, years=4, crew_weeks=4, lead_times=True)
    broken = violations(fleet, request, {"A": 2027, "B": 2027, "D": 2027, "C": 2028})
    assert [line.split(":")[0] for line in broken] == ["budget 2027", "crews north 2028", "spares large"]
    assert violations(fleet, request, {"A": 2027, "B": 2028, "D": 2027}) == []

from dataclasses import replace

from renewal.fleet import Transformer
from renewal.plan import lp_bound, plan
from renewal.request import Request


def unit(tid, substation, cof):
    return Transformer(tid, substation, "north", "small", 55, 300, cof, 50, 0.0)


def test_per_unit_outage_rows_tighten_the_lp_bound_and_keep_the_optimum():
    fleet = [unit("A", "S1", 4000), unit("B", "S1", 1000), unit("C", "S1", 900), unit("D", "S2", 3000)]
    strong = Request(budget=1300, years=1, window=10, outage_cost=600, link="per-unit")
    weak = replace(strong, link="aggregated")
    assert lp_bound(fleet, strong) < lp_bound(fleet, weak) - 1
    assert abs(plan(fleet, strong).value - plan(fleet, weak).value) < 1e-6

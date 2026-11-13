import pytest
from scipy.stats import weibull_min

from register import Valve, rank_by_risk, risk


def pof(v: Valve) -> float:
    curve = weibull_min(c=v.beta, scale=v.eta)
    return 1 - curve.sf(v.age + 1) / curve.sf(v.age)


def test_with_equal_curves_and_ages_the_costlier_valve_ranks_first():
    valves = [Valve("V1", 30, 2.5, 40, 300), Valve("V2", 30, 2.5, 40, 900), Valve("V3", 30, 2.5, 40, 600)]
    assert rank_by_risk(valves) == ["V2", "V3", "V1"]


def test_an_old_survivor_is_ranked_by_its_conditional_chance():
    old, young = Valve("OLD", 60, 3.0, 40, 500), Valve("YOUNG", 20, 3.0, 40, 1_000)
    assert rank_by_risk([young, old]) == ["OLD", "YOUNG"]


def test_a_likely_failure_can_outrank_a_costlier_one():
    worn, costly = Valve("WORN", 45, 3.5, 40, 400), Valve("COSTLY", 10, 3.5, 40, 3_000)
    assert pof(worn) * worn.cof > pof(costly) * costly.cof
    assert rank_by_risk([costly, worn]) == ["WORN", "COSTLY"]


def test_risk_is_the_chance_of_failing_next_year_times_the_cost():
    v = Valve("V9", 50, 4.0, 40, 700)
    assert risk(v) == pytest.approx(pof(v) * 700, rel=1e-9)

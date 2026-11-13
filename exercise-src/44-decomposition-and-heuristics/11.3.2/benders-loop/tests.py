import itertools

import pytest

from station_benders import benders, pumping_cut

STATIONS = {
    "hill": {"build": 90, "capacity": 60, "energy": 2.0, "refill": 5},
    "river": {"build": 60, "capacity": 40, "energy": 3.0, "refill": 4},
    "lake": {"build": 150, "capacity": 80, "energy": 1.5, "refill": 8},
    "quarry": {"build": 40, "capacity": 30, "energy": 2.5, "refill": 2},
}


def cheapest(stations, demand, limit, price):
    """The monolithic answer, by trying every plan."""
    from ortools.math_opt.python import mathopt
    x = {j: mathopt.Model().add_binary_variable(name=j) for j in stations}
    best = None
    for bits in itertools.product((0, 1), repeat=len(stations)):
        plan = dict(zip(stations, bits))
        pumping, _ = pumping_cut(stations, demand, limit, price, plan, x)
        total = sum(s["build"] * plan[j] for j, s in stations.items()) + pumping
        best = total if best is None else min(best, total)
    return best


def test_a_district_where_building_never_pays():
    costly = {j: {**s, "build": 5000} for j, s in STATIONS.items()}
    cost, plan, history = benders(costly, 100, 500, 3.2)
    assert cost == pytest.approx(320.0)
    assert plan == {j: 0 for j in STATIONS}


def test_the_loop_reaches_the_cheapest_plan_of_all():
    for price in (6.0, 4.0, 3.2):
        cost, plan, history = benders(STATIONS, 100, 500, price)
        assert cost == pytest.approx(cheapest(STATIONS, 100, 500, price), abs=1e-3), price
        assert history[-1][0] == pytest.approx(cost, abs=1e-3), price


def test_the_best_cost_never_rises():
    for price in (6.0, 4.0, 3.2):
        cost, _, history = benders(STATIONS, 100, 500, price)
        assert len(history) >= 2 and history[-1][1] == pytest.approx(cost), price
        uppers = [upper for _, upper in history]
        assert all(b <= a + 1e-9 for a, b in zip(uppers, uppers[1:])), price
        assert all(lower <= upper + 1e-6 for lower, upper in history), price

import itertools

import pytest
from ortools.math_opt.python import mathopt

from pump_cut import pumping_cut

STATIONS = {
    "hill": {"capacity": 60, "energy": 2.0, "refill": 5},
    "river": {"capacity": 40, "energy": 3.0, "refill": 4},
    "lake": {"capacity": 80, "energy": 1.5, "refill": 8},
}


def master_vars():
    model = mathopt.Model(name="stations")
    return {j: model.add_binary_variable(name=j) for j in STATIONS}


def at(cut, x, plan):
    return mathopt.evaluate_expression(cut + 0, {x[j]: float(plan[j]) for j in x})


def test_with_nothing_built_the_district_buys_all_its_water():
    x = master_vars()
    none = {j: 0 for j in STATIONS}
    cost, cut = pumping_cut(STATIONS, 100, 500, 6.0, none, x)
    assert cost == pytest.approx(600.0)
    assert at(cut, x, none) == pytest.approx(600.0)


def test_the_cut_is_exact_at_the_plan_it_came_from():
    x = master_vars()
    plan = {"hill": 1, "river": 0, "lake": 1}
    cost, cut = pumping_cut(STATIONS, 100, 500, 6.0, plan, x)
    # need 100 + 5 + 8 = 113: lake 80 at 1.5, hill 33 at 2.0
    assert cost == pytest.approx(80 * 1.5 + 33 * 2.0)
    assert at(cut, x, plan) == pytest.approx(cost)


def test_the_cut_never_claims_more_than_another_plan_costs():
    x = master_vars()
    base = {"hill": 1, "river": 1, "lake": 0}
    cost, cut = pumping_cut(STATIONS, 100, 500, 6.0, base, x)
    assert at(cut, x, base) == pytest.approx(cost) and cost > 0
    for bits in itertools.product((0, 1), repeat=len(STATIONS)):
        other = dict(zip(STATIONS, bits))
        other_cost, _ = pumping_cut(STATIONS, 100, 500, 6.0, other, x)
        assert at(cut, x, other) <= other_cost + 1e-6, other


def test_a_binding_purchase_limit_counts_in_the_cut():
    x = master_vars()
    plan = {"hill": 1, "river": 1, "lake": 0}
    # need 109: hill 60 at 2.0, then 30 bought at 2.5 beats river at 3.0, and river takes the last 19
    cost, cut = pumping_cut(STATIONS, 100, 30, 2.5, plan, x)
    assert cost == pytest.approx(60 * 2.0 + 30 * 2.5 + 19 * 3.0)
    assert at(cut, x, plan) == pytest.approx(cost)

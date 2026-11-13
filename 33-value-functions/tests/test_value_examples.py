"""The module 33 examples: benefit measures, normalization, swing weights and the CIPT value function."""

import pytest
from ortools.math_opt.python import mathopt

from benefits import CUSTOMERS_SERVED, Outage, earliest_measures, failures_avoided, measures, reliability_indices
from gridcap import generate
from value_function import (MEASURES, REFERENCE, SWING_RATINGS, WEIGHTS, exchange_rates, npv_equivalent,
                            ranking, raw, swing_weights, value, value_expression, value_table)


@pytest.fixture(scope="module")
def tiny():
    return generate("tiny")


@pytest.fixture(scope="module")
def small():
    return generate("small")


def test_indices_skip_momentary_outages_and_caidi_is_saidi_over_saifi():
    log = [Outage(1_000, 60), Outage(500, 5), Outage(2_000, 30)]
    got = reliability_indices(log, 10_000)
    assert got["SAIFI"] == pytest.approx(0.3)
    assert got["SAIDI"] == pytest.approx((60_000 + 60_000) / 10_000)
    assert got["CAIDI"] == pytest.approx(got["SAIDI"] / got["SAIFI"])


def test_the_lesson_outage_log(tiny):
    log = [Outage(12_000, 240), Outage(4_000, 300), Outage(9_000, 3), Outage(1_500, 180),
           Outage(400, 360), Outage(6_000, 90), Outage(20_000, 2), Outage(1_200, 150)]
    got = reliability_indices(log, CUSTOMERS_SERVED)
    assert got["SAIFI"] == pytest.approx(25_100 / 600_000)
    assert got["SAIDI"] == pytest.approx(5_214_000 / 600_000)


def test_a_later_replacement_avoids_fewer_failures(small):
    for p in small.projects:
        starts = list(p.starts())
        if len(starts) > 1 and p.intervention in ("replace", "rebuild", "underground"):
            assert failures_avoided(small, p, starts[0]) > failures_avoided(small, p, starts[-1])


def test_each_measure_ranks_tiny_differently(tiny):
    table = earliest_measures(tiny)
    tops = {k: ranking({p: getattr(m, f) for p, m in table.items()})[0] for k, (f, _) in MEASURES.items()}
    assert tops == {"reliability": "P003", "safety": "P006", "environmental": "P006", "financial": "P004"}


def test_normalized_values_ignore_units(tiny):
    scale = {"reliability": 1 / CUSTOMERS_SERVED, "safety": 7.0, "environmental": 1_000.0, "financial": 1e-3}
    reference = {k: REFERENCE[k] * scale[k] for k in REFERENCE}
    for m in earliest_measures(tiny).values():
        b = raw(m)
        assert value({k: b[k] * scale[k] for k in b}, reference, WEIGHTS) == pytest.approx(value(b, REFERENCE, WEIGHTS))


def test_swing_weights_sum_to_one_and_keep_the_ratios():
    w = swing_weights(SWING_RATINGS)
    assert sum(w.values()) == pytest.approx(1.0)
    assert w["reliability"] / w["safety"] == pytest.approx(100 / 80)


def test_exchange_rates_of_the_cipt_weights():
    rates = exchange_rates()
    assert rates["financial"] == pytest.approx(1.0)
    assert rates["safety"] == pytest.approx(80 / 60 * 5_000)
    assert rates["reliability"] * 1000 == pytest.approx(2.78, abs=0.01)


def test_rerated_wider_swing_scales_every_value_by_one_constant(small):
    wider = {**REFERENCE, "reliability": 6_000_000}
    weights = swing_weights({**SWING_RATINGS, "reliability": 200})
    for m in earliest_measures(small).values():
        b = raw(m)
        assert value(b, wider, weights) == pytest.approx(value(b, REFERENCE, WEIGHTS) * 260 / 360)


def test_value_table_has_one_coefficient_per_start_and_npv_equivalent_inverts(small):
    v = value_table(small)
    assert len(v) == sum(len(p.starts()) for p in small.projects)
    p = small.project("P030")
    only_npv = {"reliability": 0.0, "safety": 0.0, "environmental": 0.0, "financial": float(p.npv[2029])}
    assert npv_equivalent(value(only_npv, REFERENCE, WEIGHTS)) == pytest.approx(p.npv[2029])


def test_the_mathopt_expression_equals_the_plan_sum(small):
    v = value_table(small)
    model = mathopt.Model()
    x = {key: model.add_binary_variable() for key in v}
    plan = {("P030", 2029), ("P006", 2030), ("P019", 2028)}
    got = mathopt.evaluate_expression(value_expression(x, v), {var: float(k in plan) for k, var in x.items()})
    assert got == pytest.approx(sum(v[k] for k in plan))
    assert measures(small, small.project("P006"), 2030).npv == 60


def test_the_depth_formula_is_the_age_path_with_no_years_of_work(tiny, small, capsys):
    from renewal_conventions import KEEP, failures_by_age_path
    from benefits import DEPTH, EVALUATION_YEARS
    capsys.readouterr()                                  # the program prints its table on import
    for portfolio in (tiny, small):
        window = tuple(range(portfolio.years[0], portfolio.years[0] + EVALUATION_YEARS))
        for p in portfolio.projects:
            a, d = portfolio.asset(p.asset_id), DEPTH[p.intervention]
            for s in p.starts():
                assert failures_by_age_path(a, window, s, 0, 1 - d) == pytest.approx(failures_avoided(portfolio, p, s))
                assert d == 1 - KEEP[p.intervention] or p.intervention in ("clear", "widen")

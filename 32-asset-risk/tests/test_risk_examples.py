"""The module 32 examples: Weibull curves, remaining life, risk and risk reduction, checked against scipy."""

import math

import pytest
from scipy.stats import weibull_min

from asset_curves import (AGE_AFTER, ages_by_year, cumulative, cumulative_hazard, density, eta_from_rul,
                          failures_next, hazard, pof_next, residual_median, risk_reduction, survival,
                          yearly_reduction)
from gridcap import generate
from risk_model import build, plan_of, risk_coefficients, solve_highs

CURVES = [(0.7, 30.0), (1.0, 12.0), (2.49, 43.1), (3.66, 57.8)]
AGES = [0.5, 5, 25, 60]


@pytest.fixture(scope="module")
def small():
    return generate("small")


@pytest.mark.parametrize("beta,eta", CURVES)
def test_the_curve_functions_match_scipy(beta, eta):
    curve = weibull_min(c=beta, scale=eta)
    for t in AGES:
        assert cumulative(t, beta, eta) == pytest.approx(curve.cdf(t))
        assert survival(t, beta, eta) == pytest.approx(curve.sf(t))
        assert density(t, beta, eta) == pytest.approx(curve.pdf(t))
        assert hazard(t, beta, eta) == pytest.approx(curve.pdf(t) / curve.sf(t))
        assert cumulative_hazard(t, beta, eta) == pytest.approx(-curve.logsf(t))


@pytest.mark.parametrize("beta,eta", CURVES)
def test_next_year_pof_is_conditional_and_matches_the_hazard_form(beta, eta):
    curve = weibull_min(c=beta, scale=eta)
    for a in AGES:
        assert pof_next(a, beta, eta) == pytest.approx(1 - curve.sf(a + 1) / curve.sf(a))
        assert pof_next(a, beta, eta) == pytest.approx(1 - math.exp(-failures_next(a, beta, eta)))
        assert failures_next(a, beta, eta) >= pof_next(a, beta, eta)


@pytest.mark.parametrize("beta,eta", CURVES)
def test_the_median_remaining_life_halves_the_survival(beta, eta):
    curve = weibull_min(c=beta, scale=eta)
    for a in AGES:
        m = residual_median(a, beta, eta)
        assert curve.sf(a + m) / curve.sf(a) == pytest.approx(0.5)
        assert residual_median(a, beta, eta_from_rul(a, 7.0, beta)) == pytest.approx(7.0)


def test_shape_one_has_a_flat_hazard_and_shape_above_one_a_rising_one():
    assert hazard(5, 1.0, 40) == pytest.approx(hazard(60, 1.0, 40))
    assert hazard(60, 3.5, 40) > hazard(5, 3.5, 40)
    assert hazard(60, 0.7, 40) < hazard(5, 0.7, 40)


def test_the_tiny_numbers_the_pages_quote():
    tiny = generate("tiny")
    a = tiny.asset("A006")
    assert pof_next(a.age, a.weibull_beta, a.weibull_eta) == pytest.approx(0.0947, abs=5e-5)
    a4 = tiny.asset("A004")
    assert a4.rul == 1
    assert residual_median(a4.age, a4.weibull_beta, a4.weibull_eta) == pytest.approx(17.6, abs=0.05)


def test_work_resets_the_age_in_the_year_after_it_ends():
    ages = ages_by_year(50, tuple(range(2027, 2033)), 2028, 2, 0.0)
    assert ages == {2027: 50, 2028: 51, 2029: 52, 2030: 0.0, 2031: 1.0, 2032: 2.0}
    ages = ages_by_year(40, (2027, 2028, 2029), 2027, 1, 0.5)
    assert ages == {2027: 40, 2028: 20.5, 2029: 21.5}


def test_no_risk_is_removed_before_the_work_ends_and_some_is_after(small):
    p = small.project("P024")
    a = small.asset(p.asset_id)
    cut = yearly_reduction(a, tuple(range(2027, 2037)), 2028, p.duration, AGE_AFTER[p.intervention])
    assert cut[2027] == cut[2028] == cut[2029] == 0
    assert all(cut[y] > 0 for y in range(2030, 2037))


def test_a_later_start_removes_less_over_the_window(small):
    rr = risk_coefficients(small)
    assert rr["P024", 2028] > rr["P024", 2029] > rr["P024", 2030]
    assert rr["P024", 2028] == pytest.approx(1347, abs=0.5)


def test_undiscounted_coefficient_is_the_plain_sum(small):
    p = small.project("P019")
    a = small.asset(p.asset_id)
    window = tuple(range(2027, 2037))
    assert risk_reduction(a, window, 2028, 1, 0.0) == pytest.approx(sum(yearly_reduction(a, window, 2028, 1, 0.0).values()))


def test_the_risk_plan_respects_the_rules_and_beats_the_npv_plan_on_risk(small):
    rr = risk_coefficients(small)
    npv = {(p.project_id, t): p.npv[t] for p in small.projects for t in p.starts()}
    plans = {}
    for name, objective in (("npv", npv), ("rr", rr)):
        sm = build(small, objective)
        plans[name] = plan_of(sm, solve_highs(sm.model))
    for plan in plans.values():
        assert all(p.project_id in plan for p in small.projects if p.must_do)
        spend = {y: 0 for y in small.years}
        for pid, t in plan.items():
            for y, amount in small.project(pid).spend(t).items():
                spend[y] += amount
        assert all(spend[y] <= small.budget[y] for y in small.years)
    assert sum(rr[k] for k in plans["rr"].items()) > sum(rr[k] for k in plans["npv"].items())
    assert sum(npv[k] for k in plans["npv"].items()) > sum(npv[k] for k in plans["rr"].items())

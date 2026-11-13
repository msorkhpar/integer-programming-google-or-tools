"""The module 31 examples: discounting, escalation, annuities, and GridCap's NPV table rebuilt."""

import numpy_financial as npf
import pytest

from coefficients import coefficient_table
from finance import (annuity_factor, discount_factor, equivalent_annual_cost, escalate, npv_by_start_year,
                     present_value, real_rate, start_year_flows)
from gridcap import generate
from gridcap_assumptions import benefit_assumptions


def test_present_value_matches_numpy_financial_from_the_first_year():
    flows = {2027: -1_200, **{y: 180 for y in range(2028, 2038)}}
    assert present_value(flows, 0.07, 2027) == pytest.approx(npf.npv(0.07, [flows[y] for y in sorted(flows)]))
    assert present_value(flows, 0.07, 2027) == pytest.approx(64.24, abs=0.005)


def test_one_payment_three_years_out_and_back():
    today = 1_000 * discount_factor(0.07, 3)
    assert today == pytest.approx(816.30, abs=0.005)
    assert escalate(today, 0.07, 3) == pytest.approx(1_000)


def test_the_ranking_flips_at_the_crossover_rate():
    clearing, undergrounding = [-500] + [150] * 5, [-500] + [60] * 20
    crossover = npf.irr([a - b for a, b in zip(clearing + [0] * 15, undergrounding)])
    assert crossover == pytest.approx(0.0766, abs=5e-5)
    assert npf.npv(0.07, undergrounding) > npf.npv(0.07, clearing)
    assert npf.npv(0.10, clearing) > npf.npv(0.10, undergrounding)


def test_real_at_real_equals_nominal_at_nominal_and_the_mixes_do_not():
    p = generate("small").project("P022")
    inflation, real = 0.025, 0.04
    nominal = (1 + real) * (1 + inflation) - 1
    real_flows = {2028 + k: -c for k, c in enumerate(p.cost_profile)}
    nominal_flows = {y: escalate(a, inflation, y - 2027) for y, a in real_flows.items()}
    consistent = present_value(real_flows, real, 2027)
    assert present_value(nominal_flows, nominal, 2027) == pytest.approx(consistent)
    assert present_value(nominal_flows, real, 2027) < consistent < present_value(real_flows, nominal, 2027)
    assert real_rate(nominal, inflation) == pytest.approx(real)


def test_annuity_factor_matches_numpy_financial():
    assert 100 * annuity_factor(0.07, 20) == pytest.approx(npf.pv(0.07, 20, -100))
    assert equivalent_annual_cost(1_000, 0.07, 20) == pytest.approx(-npf.pmt(0.07, 20, 1_000))
    assert annuity_factor(0.0, 12) == 12


def test_replacement_beats_repair_on_eac_though_repair_has_the_lower_lifecycle_cost():
    replace = 1_970 + 25 * annuity_factor(0.07, 40) + present_value({20: 300}, 0.07, 0)
    repair = 290 + 150 * annuity_factor(0.07, 10)
    assert repair < replace
    assert equivalent_annual_cost(replace, 0.07, 40) < equivalent_annual_cost(repair, 0.07, 10)
    chain = present_value({0: repair, 10: repair, 20: repair, 30: repair}, 0.07, 0)
    assert replace < chain


def test_start_year_flows_shift_the_profile():
    assert start_year_flows((360, 720, 1470), {0: 1_000}, 2028) == {2028: 640, 2029: -720, 2030: -1470}


@pytest.mark.parametrize("size", ["tiny", "small", "medium"])
def test_the_rebuilt_table_equals_gridcaps_stored_table(size):
    portfolio, assumptions = benefit_assumptions(size)
    stored = {(p.project_id, t): v for p in portfolio.projects for t, v in p.npv.items()}
    assert coefficient_table(portfolio, assumptions, portfolio.discount_rate) == stored


def test_replaying_the_generator_leaves_the_portfolio_unchanged():
    replayed, _ = benefit_assumptions("small")
    assert replayed.content_hash() == generate("small").content_hash()


def test_discounting_to_the_own_start_hides_the_cost_of_delay():
    costs = (360, 720, 1470)
    own = {t: present_value(start_year_flows(costs, {}, t), 0.07, t) for t in (2027, 2028, 2029)}
    common = npv_by_start_year(costs, lambda t: {}, (2027, 2028, 2029), 0.07, 2027)
    assert len({round(v, 9) for v in own.values()}) == 1
    assert common[2027] < common[2028] < common[2029]

import math

import pytest

from values import start_year_npv, yearly_pof


def test_a_new_assets_pof_is_its_first_year_failure_chance():
    assert yearly_pof(0, 2.0, 10.0) == pytest.approx(1 - math.exp(-0.01))


def test_npv_discounts_each_year_of_the_project():
    assert start_year_npv([-100, 50, 50, 50], 2027, 2027, 0.0, 0.1, 2027) == pytest.approx(
        -100 + 50 / 1.1 + 50 / 1.21 + 50 / 1.331)


def test_an_old_assets_pof_is_conditional_on_it_working():
    # R(10) = exp(-1), R(11) = exp(-1.21)
    assert yearly_pof(10, 2.0, 10.0) == pytest.approx(1 - math.exp(-0.21))


def test_a_flat_hazard_gives_the_same_pof_at_every_age():
    assert yearly_pof(10, 1.0, 10.0) == pytest.approx(1 - math.exp(-0.1))
    assert yearly_pof(30, 1.0, 10.0) == pytest.approx(1 - math.exp(-0.1))


def test_escalation_runs_from_the_price_base_year():
    assert start_year_npv([100], 2030, 2026, 0.04, 0.0, 2026) == pytest.approx(100 * 1.04 ** 4)


def test_every_start_is_discounted_to_one_valuation_date():
    assert start_year_npv([100], 2030, 2030, 0.0, 0.1, 2027) == pytest.approx(100 / 1.1 ** 3)

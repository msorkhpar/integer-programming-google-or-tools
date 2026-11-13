import numpy_financial as npf
import pytest

from valuation import value_on


def test_flows_from_the_date_match_numpy_financial():
    flows = {2026: -500, 2027: 120, 2028: 130, 2029: 140, 2030: 150}
    assert value_on(flows, 0.06, 2026) == pytest.approx(npf.npv(0.06, [-500, 120, 130, 140, 150]))


def test_years_with_no_flow_still_count_as_waiting():
    flows = {2026: -500, 2029: 300, 2031: 400}
    assert value_on(flows, 0.06, 2026) == pytest.approx(npf.npv(0.06, [-500, 0, 0, 300, 0, 400]))


def test_amounts_before_the_date_are_carried_forward():
    flows = {2026: -500, 2027: 120, 2028: 130, 2029: 140, 2030: 150}
    on_2026 = npf.npv(0.06, [-500, 120, 130, 140, 150])
    assert value_on(flows, 0.06, 2028) == pytest.approx(on_2026 * 1.06 ** 2)


def test_amounts_after_a_later_start_are_discounted_from_the_date():
    flows = {2028: -800, 2029: 450, 2030: 450}
    assert value_on(flows, 0.05, 2026) == pytest.approx(npf.npv(0.05, [0, 0, -800, 450, 450]))

import numpy_financial as npf
import pytest

from constant import constant_dollar_value

FORECAST = {2026: -1000, 2027: 300, 2028: 320, 2029: 340, 2030: 360}
ARRAY = [-1000, 300, 320, 340, 360]


def test_with_no_inflation_the_two_rates_are_one():
    assert constant_dollar_value(FORECAST, 0.08, 0.0, 2026) == pytest.approx(npf.npv(0.08, ARRAY))


def test_the_forecast_is_deflated_before_it_is_discounted():
    assert constant_dollar_value(FORECAST, 0.08, 0.03, 2026) == pytest.approx(npf.npv(0.08, ARRAY))


def test_the_real_rate_takes_inflation_out_once():
    assert constant_dollar_value(FORECAST, 0.09, 0.04, 2026) == pytest.approx(npf.npv(0.09, ARRAY))


def test_the_exact_real_rate_is_used():
    forecast = {2026 + t: (-5000 if t == 0 else 400) for t in range(31)}
    expected = npf.npv(0.08, [forecast[y] for y in sorted(forecast)])
    assert constant_dollar_value(forecast, 0.08, 0.03, 2026) == pytest.approx(expected, rel=1e-9, abs=1e-9)

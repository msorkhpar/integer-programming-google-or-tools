import pytest

from forecast import forecast_and_gain


def test_where_the_relaxation_is_whole_forecast_and_gain_agree():
    answer = forecast_and_gain([2, 2], [4, 4], 1, 2)
    assert answer["forecast"] == pytest.approx(4)
    assert answer["gain"] == pytest.approx(4)


def test_the_price_is_the_dual_value_not_the_best_ratio():
    # At 3 the best project per dollar (cost 2, worth 6) is fully funded; the price is the next one's.
    answer = forecast_and_gain([2, 4], [6, 4], 3, 4)
    assert answer["forecast"] == pytest.approx(4)
    assert answer["gain"] == pytest.approx(4)


def test_the_gain_comes_from_the_milp_not_the_relaxation():
    answer = forecast_and_gain([3, 3], [3, 3], 4, 1)
    assert answer["forecast"] == pytest.approx(1)
    assert answer["gain"] == pytest.approx(0)


def test_the_forecast_is_price_times_extra_even_past_its_range():
    answer = forecast_and_gain([2, 4], [6, 4], 1, 3)
    assert answer["forecast"] == pytest.approx(9)
    assert answer["gain"] == pytest.approx(6)
